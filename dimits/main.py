import os

from dimits.utils import download,  logger

from dimits.ttsmodel import TextToSpeechModel as ttsm
import requests
import shutil

from huggingface_hub import hf_hub_url,snapshot_download,hf_hub_download
import platform

import requests

from pathlib import Path
from huggingface_hub import HfFileSystem



class Dimits():
    """Dimits"""         
    def __init__(self, voice: str, verbose: bool = True, modelDirectory: str = None):
        """
        Initialize a new instance of Dimits with the provided voice and verbosity.

        Args:
            voice (str): The voice to use for text-to-speech.
            verbose (bool): Whether to print verbose output.
            model (str): represents the local path to the model file. If not provided (i.e., None), the default behavior is to utilize the model hosted on GitHub.

        Returns:
            None
        

        Example:
            >>> from Dimits import Dimits
            >>> dt = Dimits("en_US-amy-low")
        """
        self.verbose = verbose
       
        # Define the URL for the latest release of piper

        arch = str(self._get_os())
        if self._get_os() == 'unsupported_machine': 
            logger(err= f'{arch} Detected', verbose=verbose)
            return 

        home =  Path.home()
        
        self.voice = voice
        self.folder = 'piper'

        self._repo_id = "rhasspy/piper-voices"
      
        
        self.parent_destn = modelDirectory if modelDirectory is not None else os.path.join(home, self.folder)
        
        if not os.path.exists(self.parent_destn):
            os.mkdir(self.parent_destn)

       
        # Download the voice if it does not exist
        self._download_voice(voice)

        # Set the path to the ONNX voice file

        self.voice_onnx = voice
        self.voice_onnx = os.path.join(
        self.parent_destn, str(self.voice_onnx) + '.onnx')
        logger('Using ' + str(self.voice_onnx), verbose=verbose)

    
    @staticmethod    
    def _get_os() -> str:
        if (platform.system() in ['Windows', 'Linux']):
            return  platform.system();
        else: 
            return "unsupported_machine"

      
    @staticmethod
    def list_voice() -> list[str]:
        """
        Method `list_voice()` Lists the supported voice as per in from https://api.github.com/repos/rhasspy/piper/releases
        
        Args:
             None
        
        Returns:
             list[str] : Supported voice
        """
        
        fs = HfFileSystem()
 
        return [_.split("/")[-1].split(".")[0] for _ in fs.glob(f"{self._repo_id}/**.onnx", detail=False)]

        # return

    def _download_voice(self, name, verbose: bool = True):
        print(name)
        locale, p, pitch = name.split('-')
        lang, cc = locale.split("_")
        filename =  f"""{name}.onnx"""
        filename2 = f"""{name}.onnx.json"""
        filepath = os.path.join(self.parent_destn, filename)
        filepath2 = os.path.join(self.parent_destn, filename2)
      
        if not os.path.exists(filepath) or not os.path.exists(filepath2) :
        
            


        

            url =hf_hub_url(repo_id=self._repo_id,filename=f"{lang}/{locale}/{p}/{pitch}/{name}.onnx")
            url2 = hf_hub_url(repo_id=self._repo_id,filename=f"{lang}/{locale}/{p}/{pitch}/{name}.onnx.json")
            download(url, filepath, filename, verbose)
            download(url2, filepath2, filename2, verbose) 
            
                
           

    def text_2_audio_file(self, text: str, filename: str, directory: str, format: str = 'wav') -> str:
        r"""

        Convert the provided text to a human-sounding audio file using a text-to-speech engine, and save it to disk.

        Args:
            text (str): The text to be converted to audio.
            filename (str): The name of the output audio file, without the file extension.
            format (str): The file format of the output audio file (e.g. 'wav', 'mp3', 'ogg', etc.).
            directory (str): The directory in which to save the output audio file.
       
        Returns:
            str: The path of audio file
        
        

        Example:
            >>> from Dimits import Dimits
            >>> dt = ... #Initialize here
            >>> dt.text_to_audio("Hello World", "hello_world", "wav", "/path/to/output/directory/")
            >>> # Outputs an audio file named "hello_world.wav" in the directory "/path/to/output/directory/".

       """
        if self._get_os() == 'unsupported_machine': return
        if not os.path.exists(directory):
            os.mkdir(directory)
        filepath = os.path.join(directory, f'{filename}.{format}')
        
     
        out_bin = ttsm(self.voice_onnx).synthesize(text,length_scale=1.0, noise_scale=1.0, noise_w=1.0)
        with open(filepath, 'wb') as f:
            f.write(out_bin)

        return filepath

    def text_file_2_audio_file(self, text_file_path: str, audio_filename: str, directory: str, audio_format: str='wav', encoding='utf8', **kwargs) -> str:
        """
        Convert the provided text files to audio file

        Args:
            text_file_path (str): Path of the file to be read
            audio_filename (str): The name of the audio file to be saved
            directory (str): The directory to which audio file is extracted
            audio_format (str): The format of audio file
            encoding (str): encoding of the text file to be read utf8, utf16

        Returns:
            str: audio file path

        Example:
            >>> from dimits import Dimits 
            >>> dd = ...
            >>> dd.text_file_2_audio_file(file_path,'hello', dir,)
        """
        if self._get_os() == 'unsupported_machine': return
        with open(text_file_path, encoding=encoding) as f:
           return self.text_2_audio_file(f.readline(), audio_filename, directory, audio_format, **kwargs)


    def text_2_speech(self, text: str, engine: str = None , **kwargs: str) -> None:
        
        r"""
        Convert the provided text to human-sounding audio and play the audio file on-the-go.

        Args:
            text (str): The text to be converted to audio.
            engine (str): The text-to-speech engine to play the audio file .
                          Defaults to 'aplay'.
                        
        Returns:
            None
        

        Example:
            >>> from dimits import Dimits
            >>> dt = ... #Initialize here
            >>> dt.text_2_speech("Hello World", "aplay"")
            >>> # plays the audio to the default audio output device using the 'alsa' engine.
        """
        
        if self._get_os() == 'unsupported_machine': return
        cache_dir  = os.path.join(self.parent_destn, 'cache')
        if os.path.isdir(cache_dir):
            shutil.rmtree(cache_dir)
            os.mkdir(cache_dir)

        filepath = self.text_2_audio_file(
                       text, 'main', directory=cache_dir, )
        if platform.system() == 'Linux':
        
           os.system(f'killall {engine}')
           if engine == None: engine = 'aplay'
           
           if engine == 'aplay':
              os.system(f'{engine} {filepath}')
           else:
               pass
        elif platform.system() == 'Windows':
            if engine == None:  engine = 'System.Media.SoundPlayer'


           
            if engine == 'System.Media.SoundPlayer':
               cmd = f"""powershell (New-Object {engine} {filepath}).PlaySync()"""
               os.system(cmd )
           
    
 

