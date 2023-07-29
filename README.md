
# **Dimits - Python Bindings for Piper TTS**


Dimits is a Python library that provides an easy-to-use interface to the Piper text-to-speech (TTS) system. It utilizes the powerful Piper TTS engine, which is optimized for Raspberry Pi 4, to generate high-quality synthesized speech.
> 
## Features

* Simple Python bindings for Piper TTS
* Support for multiple languages and voices
* Compatible with Raspberry Pi 3/4 and desktop Linux systems

## Installation 📥

You can install Dimits via pip:

```sh
pip install dimits
```

This will automatically install the necessary dependencies

## Quick Start 🏃🏻‍♀️

Here's a simple example of using Dimits to synthesize speech:

```python
from dimits import Dimits

# Initialize Dimits with the desired voice model
dt = Dimits("voice-en-us-amy-low")

# Convert text to audio and play it using the aplay engine
dt.text_2_speech("Hello World", engine="aplay")
```

## Voices 🔊

Dimits supports all the voices available in the Piper TTS system. To use a specific voice, simply provide  corresponding `.onnx` file namepo initializing the `Dimits` class.

For a list of available voices and their download links, refer to the [Piper TTS repository](https://github.com/rhasspy/piper/releases/tag/v0.0.2).

## Usage 📃

### Initializing Dimits

To use Dimits, first create an instance of the `Dimits` class, providing the path to the desired voice model:

```python
from dimits import Dimits

dt = Dimits("voice-en-us-amy-low")
```

### Synthesizing Speech

To synthesize speech and play on the go, simply call the `text_2_speech` method, providing the text to be synthesized and the desired engine:

```python
dt.text_2_speech("This is a test.",engine='aplay')
```

on other hand to synthesize speech and save it to the file, call `text_2_audio_file` finction providing `file_name` `dir` and `format`

```python
dt.text_2_audio_file("Hello World", "hello_world", "/path/to/output/directory/", format="wav")
```

### Changing Voices

To change the voice used for synthesis, create a new instance of the `Dimits` class with the desired voice model:

```python
# dt = Dimits("voice-en-us-amy-low")
dt = Dimits("voice-en-us-danny-low")
```
## TODO 📝
* ~~Implement windows compatible executible to run the voice models~~
* Support for multiple audio player engine
* Benchmark
* Documentation


## License 🪪

This project is licensed under the [MIT License](LICENSE).

## Acknowledgements
Dimits is based on the work of the [Piper](https://github.com/rhasspy/piper) project by [Rhasspy](https://rhasspy.readthedocs.io/en/latest/), and is made possible by the contributions of its developers and the open source community. Without their hard work and dedication, this project would not be possible.
