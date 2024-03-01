__version__ = "0.0.21-alpha"
__author__ = "Reqeique"




from dimits.ttsmodel import TextToSpeechModel, TTSConfig
from .utils import untar, download, logger
from .main import Dimits


__all__ = ['Dimits']
