import qrcode
from PIL import Image

class SpotifyQRGenerator:

    def __init__(self, spotify_url):
        self.spotify_url = spotify_url

    async def generate_qr(self,qr_save_path):
        # Generate QR code
        img = qrcode.make(self.spotify_url)
        img.save(qr_save_path)
