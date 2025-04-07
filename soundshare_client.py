import socket
import sounddevice as sd
import threading
import time

class SoundShareServer:
    def __init__(self, host="localip", port=50007, device_name="default", samplerate=48000, channels=2, chunk_size=1024, dtype='float32'):
        self.host = host
        self.port = port
        self.device_name = device_name
        self.samplerate = samplerate
        self.channels = channels
        self.chunk_size = chunk_size
        self.dtype = dtype
        self.sock = None

    def callback(self, indata, frames, time_info, status, addr):
        if status:
            print("⚠️", status)
        if addr:
            try:
                self.sock.sendto(indata.tobytes(), addr)
            except Exception as e:
                print(f"❌ Fehler beim Senden der Audiodaten: {e}")

    def handle_client(self, conn, addr):
        print(f"✅ Verbunden mit {addr}")
        try:
            with sd.InputStream(device=self.device_name,
                                channels=self.channels,
                                samplerate=self.samplerate,
                                callback=lambda indata, frames, time_info, status: self.callback(indata, frames, time_info, status, addr),
                                blocksize=self.chunk_size,
                                dtype=self.dtype):
                print(f"📡 Sende Systemaudio an {addr}...")
                while True:
                    time.sleep(0.1)
        except Exception as e:
            print(f"❌ Fehler beim Audio-Stream an {addr}: {e}")
        finally:
            print(f"❌ Verbindung zu {addr} geschlossen.")

    def accept_clients(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Verwende UDP statt TCP
        self.sock.bind((self.host, self.port))
        print(f"🎧 Warte auf Clients auf Port {self.port}...")

        while True:
            data, addr = self.sock.recvfrom(1024)
            client_thread = threading.Thread(target=self.handle_client, args=(data, addr))
            client_thread.daemon = True
            client_thread.start()

    def cleanup(self):
        if self.sock:
            self.sock.close()

    def run(self):
        self.accept_clients()

if __name__ == "__main__":
    server = SoundShareServer()
    server.run()
