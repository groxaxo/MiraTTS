import streamlit as st
import os
import time
import re
import glob
import soundfile as sf
import numpy as np
import torch  # Added to handle Tensor operations
from datetime import datetime
from mira.model import MiraTTS

# --- Configuration ---
REFERENCE_FOLDER = "./static/reference_audio/"
OUTPUT_FOLDER = "./static/output/"
MAX_HISTORY = 5
SAMPLE_RATE = 48000  # MiraTTS is 48kHz

os.makedirs(REFERENCE_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# --- File Management ---

def cleanup_on_launch():
    """Removes stray files that don't match our naming convention on startup."""
    print("Performing startup cleanup...")
    pattern = re.compile(r'^mira_\d{8}-\d{6}\.(wav|txt)$')
    for filename in os.listdir(OUTPUT_FOLDER):
        file_path = os.path.join(OUTPUT_FOLDER, filename)
        if os.path.isfile(file_path):
            if not pattern.match(filename):
                try:
                    os.remove(file_path)
                except Exception:
                    pass

def rotate_files():
    """Keeps only the most recent MAX_HISTORY generations."""
    wav_files = sorted(
        glob.glob(os.path.join(OUTPUT_FOLDER, "mira_*.wav")),
        key=os.path.getmtime,
        reverse=True
    )
    if len(wav_files) > MAX_HISTORY:
        for wav_path in wav_files[MAX_HISTORY:]:
            try:
                os.remove(wav_path)
                txt_path = wav_path.replace(".wav", ".txt")
                if os.path.exists(txt_path):
                    os.remove(txt_path)
            except Exception as e:
                print(f"Error rotating files: {e}")

def get_history():
    """Fetches recent generations for the sidebar."""
    wav_files = sorted(
        glob.glob(os.path.join(OUTPUT_FOLDER, "mira_*.wav")),
        key=os.path.getmtime,
        reverse=True
    )
    history = []
    for wav_path in wav_files[:MAX_HISTORY]:
        txt_path = wav_path.replace(".wav", ".txt")
        preview = "No text found"
        if os.path.exists(txt_path):
            with open(txt_path, 'r', encoding='utf-8') as f:
                full = f.read().strip()
                preview = (full[:60] + '...') if len(full) > 60 else full
        history.append({'wav': wav_path, 'text': preview, 'name': os.path.basename(wav_path)})
    return history

# --- Model Engine ---

@st.cache_resource
def load_engine():
    """Loads the MiraTTS model. Cached to run only once."""
    cleanup_on_launch()
    print("Loading MiraTTS Model...")
    model = MiraTTS('YatharthS/MiraTTS')
    return model

try:
    with st.spinner("Loading MiraTTS Engine (48kHz)..."):
        tts_engine = load_engine()
except Exception as e:
    st.error(f"Failed to load engine: {e}")
    st.stop()

# --- Helpers ---

def split_text(text):
    """Splits text by sentence enders to maintain stability."""
    return [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if s.strip()]

def save_reference(uploaded_file):
    path = os.path.join(REFERENCE_FOLDER, uploaded_file.name)
    with open(path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return path

# --- UI ---

st.set_page_config(page_title="MiraTTS Studio", page_icon="🎵", layout="wide")
st.title("🎵 MiraTTS Studio")

# Initialize session state for uploader reset
if "uploader_key" not in st.session_state:
    st.session_state.uploader_key = 0

# Sidebar: Configuration
with st.sidebar:
    st.header("Voice Settings")
    
    # Tab selection for Voice
    tab_exist, tab_new = st.tabs(["Select Voice", "Upload New"])
    selected_ref_path = None
    
    with tab_exist:
        refs = [f for f in os.listdir(REFERENCE_FOLDER) if f.endswith(('.wav', '.mp3', '.ogg'))]
        if refs:
            choice = st.selectbox("Choose Reference:", refs)
            selected_ref_path = os.path.join(REFERENCE_FOLDER, choice)
            st.audio(selected_ref_path)
        else:
            st.info("No voices found. Upload one!")
            
    with tab_new:
        up_file = st.file_uploader(
            "Upload Audio (wav/mp3)", 
            type=['wav', 'mp3', 'ogg'],
            key=f"uploader_{st.session_state.uploader_key}"
        )
        if up_file:
            save_reference(up_file)
            st.success(f"Saved {up_file.name}! Switch tabs to select it.")
            st.session_state.uploader_key += 1
            time.sleep(1)
            st.rerun()

# Main Layout
col_main, col_hist = st.columns([0.65, 0.35])

with col_main:
    st.subheader("Input Text")
    user_text = st.text_area("Type here...", height=180, placeholder="Hello! This is the new high-quality engine.")
    
    if st.button("Generate Audio", type="primary", use_container_width=True):
        if not user_text or not selected_ref_path:
            st.error("Please provide both text and a reference voice.")
        else:
            status = st.empty()
            prog = st.progress(0)
            
            try:
                # 1. Encode Voice Style
                status.info("Encoding reference voice...")
                context_tokens = tts_engine.encode_audio(selected_ref_path)
                
                # 2. Process Text (Chunked)
                sentences = split_text(user_text)
                total = len(sentences)
                
                # 3. Batch Generation
                if total > 0:
                    status.info(f"Synthesizing {total} sentences...")
                    
                    # Prepare batch inputs
                    # According to model.py, cycle() is used on contexts, so a list of 1 is fine, 
                    # but repeating it ensures safety.
                    batch_contexts = [context_tokens] * total
                    
                    # Generate (Returns a PyTorch Tensor on GPU)
                    audio_tensor = tts_engine.batch_generate(sentences, batch_contexts)
                    
                    # --- CRITICAL FIX: Convert Tensor to Numpy ---
                    # 1. Move to CPU (if on GPU)
                    # 2. Convert to Numpy
                    if hasattr(audio_tensor, 'cpu'):
                        final_audio = audio_tensor.cpu().numpy()
                    else:
                        final_audio = audio_tensor # Fallback
                        
                    # 3. Ensure Float32 for SoundFile
                    final_audio = final_audio.astype(np.float32)

                    prog.progress(80)
                    
                    # 4. Save
                    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
                    base_name = f"mira_{timestamp}"
                    wav_path = os.path.join(OUTPUT_FOLDER, f"{base_name}.wav")
                    txt_path = os.path.join(OUTPUT_FOLDER, f"{base_name}.txt")
                    
                    sf.write(wav_path, final_audio, SAMPLE_RATE)
                    
                    with open(txt_path, "w") as f:
                        f.write(user_text)
                        
                    rotate_files()
                    prog.progress(100)
                    status.success("Done!")
                    time.sleep(0.5)
                    st.rerun()
                    
            except Exception as e:
                st.error(f"Error: {e}")

# History Column
with col_hist:
    st.subheader("Recent History")
    history = get_history()
    if not history:
        st.caption("No recent generations.")
        
    for item in history:
        with st.container(border=True):
            st.markdown(f"**\"{item['text']}\"**")
            st.audio(item['wav'], format="audio/wav")
            st.caption(f"`{item['name']}`")
