import os

from dimits.utils import download, untar, logger

from dimits.ttsmodel import TextToSpeechModel as ttsm
import requests
import shutil
import platform

import requests

from pathlib import Path




class Dimits():
    """Dimits"""         
    def __init__(self, voice: str, verbose: bool = True):
        """
        Initialize a new instance of Dimits with the provided voice and verbosity.

        Args:
            voice (str): The voice to use for text-to-speech.
            verbose (bool): Whether to print verbose output.

        Returns:
            None
        

        Example:
            >>> from Dimits import Dimits
            >>> dt = Dimits("voice-en-us-amy-low")
        """
        self.verbose = verbose
        # Define the URL for the latest release of piper
        arch = str(self._get_os())
        if self._get_os() == 'unsupported_machine': 
            logger(err= f'{arch} Detected', verbose=verbose)
            return 

        home = str(Path.home())
        
        self.voice = voice
        self.folder = 'piper'
      
        
        self.parent_destn = os.path.join(home, self.folder)
        if not os.path.exists(self.parent_destn):
            os.mkdir(self.parent_destn)

       
        # Download the voice if it does not exist
        self._download_voice(voice)

        # Set the path to the ONNX voice file

        self.voice_onnx = voice
        self.voice_onnx = os.path.join(
        self.parent_destn, str(self.voice_onnx).replace('voice-', '') + '.onnx')
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
        
        releases_url = f"https://api.github.com/repos/rhasspy/piper/releases"

        response = requests.get(releases_url)

        data = response.json()

        return [[str(asset['name']).split('.')[0] for asset in release['assets'] if asset['name'].startswith('voice')] for release in data][-1]

        # return

    def _download_voice(self, name, verbose: bool = True):
        filename = f'{name}.tar.gz'
        filepath = os.path.join(self.parent_destn, filename)
        if not os.path.exists(filepath):
            filename = f'{name}.tar.gz'
            download_url = f'https://github.com/rhasspy/piper/releases/download/v0.0.2/{filename}'

            
            if type(download(download_url, filepath, filename, verbose)) is tuple:
                fp, f = tuple(download(download_url, filepath, filename, verbose))
                untar(fp, f, verbose)
            
                
           

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
           
    
 

# print(Dimits.list_voice())
# Dimits("voice-en-us-danny-low").text_2_speech(text="""
# Here is a randomly generated short story:

# It was a dark and stormy night. John was home alone, sitting in his living room reading a book. The wind howled outside as the rain pattered against the windows. Suddenly, there was a loud crash from the kitchen. John jumped up, his heart racing. What was that?

# As John slowly walked towards the kitchen, he could hear a strange skittering sound. He flipped on the light switch, but the power was out. Grabbing a flashlight from a drawer, he shined it around the room. In the beam of light, John saw the shattered remains of a flower vase on the floor.""", filename='test', directory='C:\\Users\\Ananiya\\PyProject\\PyPiperTTS\\dimits')



