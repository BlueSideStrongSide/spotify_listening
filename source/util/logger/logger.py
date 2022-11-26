import logging
from abc import ABC

class SpotifyLogger(ABC):
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.DEBUG) # <-- Dynamic

        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        ch.setFormatter(formatter)

        self.logger.addHandler((ch))



if __name__ == '__main__':
    test = SpotifyLogger()



