__version__ = "0.0.3-alpha"
__author__ = "Reqeique"




from dimits.ttsmodel import TextToSpeechModel, TTSConfig
from .utils import download, logger
from .main import Dimits


__all__ = ['Dimits']
