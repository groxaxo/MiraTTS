# MiraTTS
[MiraTTS](https://huggingface.co/YatharthS/MiraTTS) is a finetune of the excellent [Spark-TTS](https://huggingface.co/SparkAudio/Spark-TTS-0.5B) model for enhanced realism and stability performing on par with closed source models. 
This repository also heavily optimizes Mira with [Lmdeploy](https://github.com/InternLM/lmdeploy) and boosts quality by using [FlashSR](https://github.com/ysharma3501/FlashSR) to generate high quality audio at over **100x** realtime!

https://github.com/user-attachments/assets/262088ae-068a-49f2-8ad6-ab32c66dcd17

## Key benefits
- Incredibly fast: Over 100x realtime by using Lmdeploy and batching.
- High quality: Generates clear and crisp 48khz audio outputs which is much higher quality then most models.
- Memory efficient: Works within 6gb vram.
- Low latency: Latency can be low as 100ms.
- Advanced text normalization: Automatically handles URLs, emails, phone numbers, money, units, and special characters (inspired by [Kokoro-FastAPI](https://github.com/remsky/Kokoro-FastAPI)).

## Usage
Simple 1 line installation:
```
uv pip install git+https://github.com/ysharma3501/MiraTTS.git
```

Running the model(bs=1):
```python
from mira.model import MiraTTS
from IPython.display import Audio
mira_tts = MiraTTS('YatharthS/MiraTTS') ## downloads model from huggingface

file = "reference_file.wav" ## can be mp3/wav/ogg or anything that librosa supports
text = "Alright, so have you ever heard of a little thing named text to speech? Well, it allows you to convert text into speech! I know, that's super cool, isn't it?"

context_tokens = mira_tts.encode_audio(file)
audio = mira_tts.generate(text, context_tokens)

Audio(audio, rate=48000)
```

### Text Normalization
MiraTTS includes advanced text normalization that automatically handles:
- URLs (e.g., "https://example.com" → "https example dot com")
- Emails (e.g., "user@example.com" → "user at example dot com")
- Phone numbers (e.g., "555-123-4567" → spoken format)
- Money amounts (e.g., "$50.99" → "fifty dollars and ninety-nine cents")
- Numbers and units (e.g., "10KB" → "ten kilobytes")
- Special characters and symbols

By default, text normalization is enabled. To customize or disable it:

```python
from mira.text_processing import NormalizationOptions

# Disable normalization
audio = mira_tts.generate(text, context_tokens, normalize=False)

# Customize normalization options
options = NormalizationOptions(
    normalize=True,
    url_normalization=True,
    email_normalization=True,
    phone_normalization=True,
    unit_normalization=False,  # Disable unit conversion
    replace_remaining_symbols=True
)
audio = mira_tts.generate(text, context_tokens, normalization_options=options)
```

You can also split and normalize text manually:
```python
from mira.text_processing import normalize_text, NormalizationOptions

# Normalize text
normalized = normalize_text("Visit https://example.com for $99!", NormalizationOptions())
# Returns: "Visit https example dot com for ninety-nine dollars!"

# Split text into sentences with normalization
sentences = mira_tts.split_text(text, normalize=True)
```

Running the model using batching: 
```python
file = "reference_file.wav" ## can be mp3/wav/ogg or anything that librosa supports
text = ["Hey, what's up! I am feeling SO happy!", "Honestly, this is really interesting, isn't it?"]

context_tokens = [mira_tts.encode_audio(file)]

audio = mira_tts.batch_generate(text, context_tokens)

Audio(audio, rate=48000)
```

Examples can be seen in the [huggingface model](https://huggingface.co/YatharthS/MiraTTS)

I recommend reading these 2 blogs to better easily understand LLM tts models and how I optimize them
- How they work: https://huggingface.co/blog/YatharthS/llm-tts-models
- How to optimize them: https://huggingface.co/blog/YatharthS/making-neutts-200x-realtime

## Training
Released training code! You can now train the model to be multilingual, multi-speaker, or support audio events on any local or cloud gpu!

Kaggle notebook: https://www.kaggle.com/code/yatharthsharma888/miratts-training

Colab notebook: https://colab.research.google.com/drive/1IprDyaMKaZrIvykMfNrxWFeuvj-DQPII?usp=sharing

## Web Interface (Streamlit)
MiraTTS now includes a user-friendly Streamlit web interface for easy voice cloning and audio generation!

### Features
- **High Fidelity:** Generates crystal clear 48kHz audio
- **Zero-Shot Cloning:** Upload a 5-10 second reference clip to clone any voice
- **Smart Batching:** Uses batch generation to synthesize long text rapidly (up to 100x realtime)
- **History System:** Automatically saves and displays the last 5 generations
- **GPU Optimized:** Caches the model in VRAM to prevent reloading on every request

### Running the Web Interface
After installing MiraTTS, you can launch the Streamlit interface:

```bash
streamlit run app_mira.py
```

Then open your browser to `http://localhost:8501` to access the interface.

### First Run Note
On the very first launch, the app will download the MiraTTS model weights (~2-3 GB) from Hugging Face. This happens automatically and may take a few minutes depending on your internet speed.

### Prerequisites
- **Hardware:** NVIDIA GPU with at least 6GB VRAM (required for Lmdeploy/FlashSR)
- **System:** FFmpeg installed (`sudo apt install ffmpeg` on Linux)
- **Python:** Version 3.10 or higher

## Next steps
- [x] Release code and model
- [x] Release training code
- [x] Add web interface (Streamlit)
- [ ] Support low latency streaming
- [ ] Release native 48khz bicodec
      
## Final notes
Thanks very much to the authors of Spark-TTS and unsloth. Thanks for checking out this repository as well.

Stars would be well appreciated, thank you.

Email: yatharthsharma3501@gmail.com
