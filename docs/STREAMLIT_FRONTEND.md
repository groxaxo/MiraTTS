# MiraTTS Streamlit Frontend Guide

This guide covers the Streamlit web interface for MiraTTS, providing an easy-to-use interface for voice cloning and audio generation.

## Overview

The MiraTTS Streamlit frontend (based on [MiraTTSstreamlit](https://github.com/ArtificialAnaleptic/MiraTTSstreamlit)) provides a user-friendly web interface for:

- Uploading and managing reference audio files
- Generating high-quality 48kHz audio with voice cloning
- Batch processing long text with automatic sentence splitting
- Viewing generation history with saved audio and text

## Features

### CPU Optimized
- Uses INT4 quantized ONNX model for efficient CPU inference
- 2x faster inference and 15x less memory usage
- Runs efficiently without requiring high-end GPU
- Ideal for accessibility and resource-constrained environments

### High Fidelity Audio
- Generates crystal clear 48kHz audio output
- Uses FlashSR for audio super-resolution
- Over 100x realtime generation speed with batching

### Zero-Shot Voice Cloning
- Upload a 5-10 second reference audio clip
- Supports WAV, MP3, and OGG formats
- Instantly clone any voice without training

### Smart Text Processing
- Automatically splits long text by sentences
- Prevents model hallucinations on long paragraphs
- Uses batch generation for optimal performance

### History System
- Automatically saves the last 5 generations
- Stores both audio (WAV) and text (TXT) files
- Easy playback and review of previous generations

### GPU Optimization
- Caches model in VRAM for fast generation (when GPU is available)
- Also runs efficiently on CPU with ONNX Runtime
- Prevents model reloading on every request
- Efficient memory management

## Prerequisites

### Hardware Requirements
- **CPU**: Any modern CPU (optimized for CPU inference with INT4 ONNX)
- **GPU**: Optional - NVIDIA GPU with 6GB+ VRAM for faster processing
- **RAM**: 4GB+ recommended (8GB+ for optimal performance)
- **Storage**: ~3GB for INT4 ONNX model weights and cache

### Software Requirements
- **Python**: 3.10 or higher (3.12 recommended)
- **FFmpeg**: Required for audio processing
- **CUDA**: Optional - for GPU acceleration (not required for CPU mode)

## Installation

### 1. Install System Dependencies

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install ffmpeg
```

**Windows:**
1. Download FFmpeg from [gyan.dev](https://www.gyan.dev/ffmpeg/builds/)
2. Extract and add the `bin` folder to System PATH
3. Install "Desktop development with C++" from Visual Studio Installer if needed

### 2. Install MiraTTS

```bash
pip install git+https://github.com/groxaxo/MiraTTS.git
```

Or with `uv` (recommended):
```bash
uv pip install git+https://github.com/groxaxo/MiraTTS.git
```

## Usage

### Starting the Web Interface

Navigate to your MiraTTS installation directory and run:

```bash
streamlit run app_mira.py
```

The application will start and display a URL (typically `http://localhost:8501`). Open this URL in your web browser.

### First Launch

On the first run, MiraTTS will:
1. Download INT4 ONNX model weights (~1-2 GB) from Hugging Face
2. Initialize the ONNX Runtime engine
3. Set up the audio codec

This process may take 3-5 minutes depending on your internet speed. The INT4 quantized model is significantly smaller than the original model. Watch the terminal for progress.

### Using the Interface

#### 1. Upload a Reference Voice

**Option A: Upload New Audio**
1. Click the "Upload New" tab in the sidebar
2. Click "Browse files" or drag a WAV/MP3/OGG file
3. Wait for upload confirmation
4. Switch to "Select Voice" tab to use it

**Option B: Select Existing Voice**
1. Click the "Select Voice" tab
2. Choose from previously uploaded voices
3. Preview the audio by clicking play

#### 2. Generate Audio

1. Type or paste your text in the main text area
2. Ensure a reference voice is selected
3. Click "Generate Audio"
4. Watch the progress bar for status updates
5. The generated audio will appear in the history column

#### 3. View History

The right sidebar shows your last 5 generations:
- Preview text (first 60 characters)
- Playback audio directly in browser
- Full timestamp in filename

## File Structure

```
MiraTTS/
├── app_mira.py              # Main Streamlit application
├── static/
│   ├── reference_audio/     # Uploaded reference voices
│   └── output/              # Generated audio files
│       ├── mira_YYYYMMDD-HHMMSS.wav
│       └── mira_YYYYMMDD-HHMMSS.txt
└── ...
```

## Configuration

### Adjusting Settings

You can modify these constants in `app_mira.py`:

```python
REFERENCE_FOLDER = "./static/reference_audio/"  # Reference audio location
OUTPUT_FOLDER = "./static/output/"              # Output location
MAX_HISTORY = 5                                  # Number of generations to keep
SAMPLE_RATE = 48000                              # Audio sample rate (48kHz)
```

### Model Parameters

To use a different model or adjust initialization in `app_mira.py`:

```python
# Default: INT4 ONNX model (CPU optimized)
model = MiraTTS()

# Or use the original FP32 model
model = MiraTTS('YatharthS/MiraTTS')

# Or use GPU acceleration with ONNX
model = MiraTTS(device='cuda')
```

## Troubleshooting

### GPU Not Detected (Optional)

**Note:** GPU is optional - the app runs efficiently on CPU with the INT4 ONNX model.

**Linux:**
```bash
nvidia-smi  # Check if GPU is visible
```

**Windows:**
If you want to use GPU and PyTorch doesn't detect it, install the CUDA-specific version:
```bash
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu121
```

### Model Download Fails

If the Hugging Face download fails:
1. Check your internet connection
2. Try using a VPN if region-blocked
3. Manually download from [uetuluk2/MiraTTS-onnx-int4](https://huggingface.co/uetuluk2/MiraTTS-onnx-int4)
4. Point to local model: `MiraTTS('/path/to/local/model')`

### Out of Memory Errors

If you get OOM errors (rare with CPU mode):
1. Reduce batch size by limiting text length
2. If using GPU: clear VRAM by restarting the application
3. Close other memory-intensive applications
4. The INT4 ONNX model uses significantly less memory than the full model

### Audio Quality Issues

For best results:
- Use 5-10 second reference clips (clear, noise-free)
- Ensure reference audio has consistent volume
- Avoid background noise in reference audio
- Use WAV format for reference (highest quality)

### Port Already in Use

If port 8501 is busy, specify a different port:
```bash
streamlit run app_mira.py --server.port 8502
```

## Tips for Best Results

### Reference Audio
- **Length**: 5-10 seconds ideal
- **Quality**: Clear, noise-free recording
- **Content**: Natural speech, not singing or whispering
- **Format**: WAV preferred, MP3/OGG acceptable

### Input Text
- Use proper punctuation for natural pauses
- Keep sentences reasonable length (not > 100 words)
- The app automatically splits by sentences
- Special characters and numbers are handled automatically

### Performance
- Longer text benefits from batch processing
- Generation is faster after the first run (model cached)
- Close other GPU applications for best performance

## Advanced Usage

### Custom Text Normalization

The app uses MiraTTS's built-in normalization by default. For manual control, modify the generation code in `app_mira.py`:

```python
from mira.text_processing import NormalizationOptions

options = NormalizationOptions(
    normalize=True,
    url_normalization=True,
    email_normalization=True,
    phone_normalization=True,
    unit_normalization=False,
    replace_remaining_symbols=True
)

# Use with generate call
audio = tts_engine.generate(text, context_tokens, normalization_options=options)
```

### Programmatic API

You can use MiraTTS programmatically without the web interface:

```python
from mira.model import MiraTTS

# Initialize with default INT4 ONNX model (CPU optimized)
mira = MiraTTS()

# Or use GPU
# mira = MiraTTS(device='cuda')

# Encode reference
context = mira.encode_audio('reference.wav')

# Generate
audio = mira.generate("Hello world!", context)

# Or batch generate
texts = ["First sentence.", "Second sentence."]
contexts = [context] * len(texts)
audio = mira.batch_generate(texts, contexts)
```

## Credits

- **MiraTTS**: [Yatharth Sharma](https://github.com/ysharma3501) - Original creator
- **Streamlit Frontend**: [ArtificialAnaleptic](https://github.com/ArtificialAnaleptic/MiraTTSstreamlit)
- **Base Model**: Spark-TTS Team
- **INT4 ONNX Optimization**: [uetuluk2](https://huggingface.co/uetuluk2)
- **This Fork**: [groxaxo/MiraTTS](https://github.com/groxaxo/MiraTTS) - CPU-optimized version

## License

This frontend follows the same license as MiraTTS. Please see the main repository LICENSE file.

## Support

For issues or questions:
- MiraTTS Issues: https://github.com/groxaxo/MiraTTS/issues
- Original Frontend: https://github.com/ArtificialAnaleptic/MiraTTSstreamlit/issues
