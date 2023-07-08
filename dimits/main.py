import os

from dimits.utils import download, untar, logger
import requests

import platform

import requests
from tqdm import tqdm

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
        arch = str(self._get_arch())
        if self._get_arch() == 'unsupported_machine': 
            logger(err= f'{arch} Detected', verbose=verbose)
            
        if self._get_arch() == 'unsupported_machine': return
        logger(msg= f'{arch} Detected', verbose=verbose)

        home = str(Path.home())
        
        self.voice = voice
        self.folder = 'piper'
        self.piper_bin_zip = f'piper_{arch}.tar.gz'
        
        self.parent_destn = os.path.join(home, self.folder)
        if not os.path.exists(self.parent_destn):
            os.mkdir(self.parent_destn)

        # Set the full filepath for the downloaded file
        self.filepath = os.path.join(self.parent_destn, self.piper_bin_zip)

        #Download the binary if it does not exist
        if not os.path.exists(self.filepath):
            latest_releases_url = f"https://api.github.com/repos/rhasspy/piper/releases/latest"

        # Fetch the latest release information from Github API
            latest_releases_response = requests.get(latest_releases_url)
    
            # Parse the latest version number from the API response
            if latest_releases_response.status_code == 200:
                # Parse the api JSON to extract the release version
                release_info = latest_releases_response.json()
                latest_release = release_info["tag_name"]

            # Set the URL for the binary download
            binary_url = f"https://github.com/rhasspy/piper/releases/download/{latest_release}/{self.piper_bin_zip}"

            # Download the binary file and check for errors
            response = download(binary_url, self.filepath,
                                self.piper_bin_zip, verbose=verbose)

            # If the response is a tuple, extract the filepath and filename and untar the file
            if type(response) is tuple:
                fp, f = response
                untar(fp, f, verbose=verbose)
            # If the response is an integer, log an error message
            elif type(response) is int:
                logger(err=f"Can't Download {self.piper_bin_zip}", verbose=verbose)

        # Set the path to the piper binary file
        self.piper_binary = os.path.join(self.parent_destn, 'piper', 'piper')

        # print(self.binary)

        # Download the voice if it does not exist
        self._download_voice(voice)

        # Set the path to the ONNX voice file

        self.voice_onnx = voice
        self.voice_onnx = os.path.join(
        self.parent_destn, str(self.voice_onnx).replace('voice-', '') + '.onnx')
        logger('Using' + str(self.voice_onnx), verbose=verbose)

    
    @staticmethod    
    def _get_arch(_: str = '') -> str:

        if platform.system() == 'Linux':
            if platform.machine() == 'aarch64':
                return 'arm64'
            elif platform.machine() == 'amd64' or platform.machine() == 'x86_64':
                return 'amd64'
            elif platform.machine().startswith('armv7'):

                return 'armv7'
        else :

            return ('unsupported_machine')
      
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
            
                
           

    def text_2_audio_file(self, text: str, filename: str, directory: str, format: str = 'wav', **kwargs: str) -> str:
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
        if self._get_arch() == 'unsupported_machine': return
        if not os.path.exists(directory):
            os.mkdir(directory)
        filepath = os.path.join(directory, f'{filename}.{format}')

        param = (' ').join(
            list([f'--{_} {__}'for _, __ in tuple(kwargs.items())]))
        command = f"""echo \"{text}\" |sudo {self.piper_binary} --model {self.voice_onnx} --output_file {filepath} {param}"""
        logger(command, verbose=self.verbose)
        os.system(command)

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
        if self._get_arch() == 'unsupported_machine': return
        with open(text_file_path, encoding=encoding) as f:
           return self.text_2_audio_file(f.readline(), audio_filename, directory, audio_format, **kwargs)


    def text_2_speech(self, text: str, engine: str = 'aplay', **kwargs: str) -> None:
        
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
        if self._get_arch() == 'unsupported_machine': return
        cache_dir  = os.path.join(self.parent_destn, 'cache')
        os.system(f'{engine} --stop')
        os.system(f'rm -rf {cache_dir}/*')
        filepath = self.text_2_audio_file(
            text, 'main', directory=cache_dir, **kwargs)
        
        
        os.system(f'{engine} {filepath}')
    
 



Dimits("voice-en-us-amy-low")


