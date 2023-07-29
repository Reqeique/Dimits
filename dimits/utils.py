import tarfile
import os

import datetime
from tqdm import tqdm
import requests
def untar(filepath,parent_destn, verbose: bool = True):
        with tarfile.open(filepath, 'r:gz') as tar:
            # Get the total size of the archive
            total_size = sum([member.size for member in tar.getmembers()])
        
            # Initialize the progress bar
            progress_bar = tqdm(desc='Extracting', total=total_size, unit='iB', unit_scale=True)
        
            # Extract each file in the archive
            for member in tar.getmembers():
                tar.extract(member, path=parent_destn)
                progress_bar.update(member.size)
        
            # Close the progress bar
            progress_bar.close()
        
            logger(f'Extracted files to {parent_destn}')

def download(url:str, filepath:str, filename:str, verbose:bool = True) -> tuple:
    folder = os.path.dirname(filepath)
    response = requests.get(url,stream=True)
    if response.status_code == 200:
        total_size = int(response.headers.get('content-length', 0))
        block_size = 1024 # 1 Kibibyte
        t = tqdm(total=total_size, unit='iB', unit_scale=True)
    
        with open(filepath, 'wb') as f:
            for data in response.iter_content(block_size):
                t.update(len(data))
                f.write(data) 
        t.close()
        logger(f'Downloaded {filename} to {filepath}.', verbose= verbose)
        return (filepath, folder)
    else:
        logger(err=f'Error downloading {filename}: {response.status_code}'
        ,verbose=verbose
        )
        return response.status_code
    



def logger(msg: str=None ,err:None= None, verbose: bool = True):
     

     if verbose == True:
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if msg != None:
           print('\033[92m[{0}] {1}\033[0m'.format(timestamp, msg))
        if err != None:
            print(f"""\033[91m[{timestamp}] {err}\033[0m""")





