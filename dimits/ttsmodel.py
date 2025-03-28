import io
import json
from dataclasses import dataclass
import logging
import wave
from pathlib import Path
from typing import List, Mapping, Optional, Sequence, Union, Dict

import numpy as np
import onnxruntime as ort 
from espeak_phonemizer import Phonemizer
from dimits.utils import logger
import soundfile as sf

_LOGGER = logging.getLogger(__name__)

_BOS = "^"
_EOS = "$"
_PAD = "_"

@dataclass
class AudioConfig:
    sample_rate: int
    quality: Optional[str] = None
    
@dataclass    
class EspeakConfig:
    voice: str
    
@dataclass
class InferenceConfig:
    noise_scale: float
    length_scale: float
    noise_w: float
    
@dataclass    
class TTSConfig:

    audio: AudioConfig
    espeak: EspeakConfig 
    inference: InferenceConfig
    
    phoneme_type: str
    phoneme_map: Mapping[str, List[int]] 
    phoneme_id_map: Mapping[str, List[int]]
    
    num_symbols: int
    num_speakers: int
    speaker_id_map: Dict
    
    piper_version: str
    
    language: Dict[str, str]
    dataset: str

    def __init__(self, **kwargs):
        self.audio = AudioConfig(**kwargs.pop('audio'))
        self.espeak = EspeakConfig(**kwargs.pop('espeak'))
        self.inference = InferenceConfig(**kwargs.pop('inference'))
        self.phoneme_type = kwargs.pop('phoneme_type', None)
        self.phoneme_map = kwargs.pop('phoneme_map')
        self.phoneme_id_map = kwargs.pop('phoneme_id_map')
        self.num_symbols = kwargs.pop('num_symbols')
        self.num_speakers = kwargs.pop('num_speakers')
        self.speaker_id_map = kwargs.pop('speaker_id_map')
        self.piper_version = kwargs.pop('piper_version', None)
        self.language = kwargs.pop('language', None)
        self.dataset = kwargs.pop('dataset', None)
       
    
# TTS model    
class TextToSpeechModel:

    def __init__(
        self,
        model_path: Union[str, Path],
        config_path: Optional[Union[str, Path]] = None,
        use_cpu: bool =True
    ):
        if config_path is None:
            config_path = f"{model_path}.json"
            
        self.config = self._load_config(config_path)
      
        self.phonemizer = Phonemizer(self.config.espeak.voice)
        self.model = ort.InferenceSession(str(model_path),sess_options=ort.SessionOptions(),
            providers= ["CPUExecutionProvider"] if(use_cpu == True) else ['CUDAExecutionProvider']
           )

    def synthesize(
        self,
        text: str,
        speaker_id: Optional[int] = None,
        length_scale: Optional[float] = None,
        noise_scale: Optional[float] = None,
        noise_w: Optional[float] = None,
    ) -> bytes:
        
        # Set default parameters if needed
        length_scale = length_scale or self.config.inference.length_scale
        noise_scale = noise_scale or self.config.inference.noise_scale
        noise_w = noise_w or self.config.inference.noise_w

        # Set default speaker
        if (self.config.num_speakers > 1) and (speaker_id is None):
            speaker_id = 0
        
        # Convert text to phonemes
        phonemes = self._text_to_phonemes(text)
        
        # Encode phonemes to ids
        phoneme_ids = self._phonemes_to_ids(phonemes)
        
        # Create model inputs
        inputs = self._create_inputs(phoneme_ids, speaker_id, noise_scale, length_scale, noise_w)

        # Run synthesis
        audio = self.model.run(None, inputs)[0].squeeze((0,1))
        
        # Convert float to int16
        audio = self._float_to_int16(audio)
        
        # Save as WAV
        wav_bytes = self._write_wav(audio, self.config.audio.sample_rate)
        
        return wav_bytes

    def _text_to_phonemes(self, text: str) -> List[str]:
        """Convert text to phoneme sequence"""
        phonemes = [_BOS] + list(self.phonemizer.phonemize(text,keep_clause_breakers=True ))
       
        return phonemes

    def _phonemes_to_ids(self, phonemes: List[str]) -> List[int]:
        """Map phonemes to ids"""
        ids = []
        for p in phonemes:
           
            if p in self.config.phoneme_id_map:
                
                ids.extend(self.config.phoneme_id_map[p])
                ids.extend(self.config.phoneme_id_map[_PAD])
            else:
                logger(f"No id found for {p}")
        ids.extend(self.config.phoneme_id_map[_EOS])
        return ids

    def _create_inputs(self, phoneme_ids, speaker_id, noise_scale, length_scale, noise_w):
        """Create model input tensors"""
        phoneme_ids = np.expand_dims(np.array(phoneme_ids,dtype=np.int64), 0)
        length = np.array([phoneme_ids.shape[1]], dtype=np.int64)
        scales = np.array([noise_scale, length_scale, noise_w],dtype=np.float32)
        speaker = np.array([speaker_id], dtype=np.int64) if speaker_id is not None else None
        
        return {
            "input": phoneme_ids,
            "input_lengths": length, 
            "scales": scales,
            "sid": speaker
        }

    def _float_to_int16(self, audio: np.ndarray) -> np.ndarray:
        """Convert audio array from float to int16"""
        audio_norm = audio * (32767 / max(0.01, np.max(np.abs(audio))))
        audio_norm = np.clip(audio_norm, -32767, 32767).astype("int16")
        return audio_norm 

    def _write_wav(self, audio: np.ndarray, sample_rate: int) -> bytes:
        """Save audio array as WAV file in memory"""
        with io.BytesIO() as fout:
            out : wave.Wave_write = wave.open(fout, "wb")
            with out:
               out.setframerate(sample_rate)
               out.setsampwidth(2)
               out.setnchannels(1)
               out.writeframes(audio.tobytes())
            # sf.write(fout, audio, samplerate=sample_rate, format="WAV", subtype="PCM_16")
            return fout.getvalue()
            
    def _load_config(self, path):
        """Load configuration from JSON file"""
        with open(path,  "r", encoding="utf-8") as f:
            data = json.load(f)
            t = TTSConfig(**data)
       
            return t
        
