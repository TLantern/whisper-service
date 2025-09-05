#!/usr/bin/env python3
"""
Lightweight Whisper v3 Service for Heroku Deployment
Optimized for phone call transcription with minimal resource usage
"""

import os
import io
import wave
import logging
import asyncio
from typing import Optional, Dict, Any
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import torch
import whisper
from pydantic import BaseModel
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Whisper v3 Transcription Service", version="1.0.0")

# CORS middleware for cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global model storage
whisper_model = None

class TranscriptionRequest(BaseModel):
    model_size: str = "base"  # tiny, base, small, medium, large-v3
    language: Optional[str] = "en"
    temperature: float = 0.0
    prompt: Optional[str] = None

class TranscriptionResponse(BaseModel):
    text: str
    avg_logprob: Optional[float] = None
    segments: Optional[list] = None
    processing_time: float

def load_whisper_model(model_size: str = "base"):
    """Load Whisper model with memory optimization"""
    global whisper_model
    
    if whisper_model is not None:
        return whisper_model
    
    try:
        logger.info(f"Loading Whisper model: {model_size}")
        
        # Use CPU for Heroku compatibility (no GPU available)
        device = "cpu"
        
        # Load model with optimizations
        whisper_model = whisper.load_model(
            model_size, 
            device=device,
            download_root="/tmp/whisper_models"  # Use tmp for Heroku
        )
        
        logger.info(f"Whisper model {model_size} loaded successfully on {device}")
        return whisper_model
        
    except Exception as e:
        logger.error(f"Failed to load Whisper model: {e}")
        raise HTTPException(status_code=500, detail=f"Model loading failed: {e}")

def convert_mulaw_to_wav(mulaw_data: bytes) -> bytes:
    """Convert mu-law encoded audio to WAV format"""
    try:
        # Convert mu-law to PCM
        pcm_data = mulaw_to_pcm(mulaw_data)
        
        # Create WAV file
        wav_buffer = io.BytesIO()
        with wave.open(wav_buffer, 'wb') as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(8000)  # 8kHz
            wav_file.writeframes(pcm_data)
        
        return wav_buffer.getvalue()
        
    except Exception as e:
        logger.error(f"Audio conversion failed: {e}")
        return mulaw_data

def mulaw_to_pcm(mulaw_data: bytes) -> bytes:
    """Convert mu-law encoded bytes to PCM"""
    # Mu-law to linear conversion table
    mulaw_table = [
        -32124, -31100, -30076, -29052, -28028, -27004, -25980, -24956,
        -23932, -22908, -21884, -20860, -19836, -18812, -17788, -16764,
        -15996, -15484, -14972, -14460, -13948, -13436, -12924, -12412,
        -11900, -11388, -10876, -10364, -9852, -9340, -8828, -8316,
        -7932, -7676, -7420, -7164, -6908, -6652, -6396, -6140,
        -5884, -5628, -5372, -5116, -4860, -4604, -4348, -4092,
        -3900, -3772, -3644, -3516, -3388, -3260, -3132, -3004,
        -2876, -2748, -2620, -2492, -2364, -2236, -2108, -1980,
        -1884, -1820, -1756, -1692, -1628, -1564, -1500, -1436,
        -1372, -1308, -1244, -1180, -1116, -1052, -988, -924,
        -876, -844, -812, -780, -748, -716, -684, -652,
        -620, -588, -556, -524, -492, -460, -428, -396,
        -372, -356, -340, -324, -308, -292, -276, -260,
        -244, -228, -212, -196, -180, -164, -148, -132,
        -120, -112, -104, -96, -88, -80, -72, -64,
        -56, -48, -40, -32, -24, -16, -8, 0,
        32124, 31100, 30076, 29052, 28028, 27004, 25980, 24956,
        23932, 22908, 21884, 20860, 19836, 18812, 17788, 16764,
        15996, 15484, 14972, 14460, 13948, 13436, 12924, 12412,
        11900, 11388, 10876, 10364, 9852, 9340, 8828, 8316,
        7932, 7676, 7420, 7164, 6908, 6652, 6396, 6140,
        5884, 5628, 5372, 5116, 4860, 4604, 4348, 4092,
        3900, 3772, 3644, 3516, 3388, 3260, 3132, 3004,
        2876, 2748, 2620, 2492, 2364, 2236, 2108, 1980,
        1884, 1820, 1756, 1692, 1628, 1564, 1500, 1436,
        1372, 1308, 1244, 1180, 1116, 1052, 988, 924,
        876, 844, 812, 780, 748, 716, 684, 652,
        620, 588, 556, 524, 492, 460, 428, 396,
        372, 356, 340, 324, 308, 292, 276, 260,
        244, 228, 212, 196, 180, 164, 148, 132,
        120, 112, 104, 96, 88, 80, 72, 64,
        56, 48, 40, 32, 24, 16, 8, 0
    ]
    
    pcm_data = bytearray()
    for byte in mulaw_data:
        pcm_value = mulaw_table[byte]
        # Convert to 16-bit signed little-endian
        pcm_data.extend(pcm_value.to_bytes(2, byteorder='little', signed=True))
    
    return bytes(pcm_data)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "model_loaded": whisper_model is not None}

@app.post("/transcribe", response_model=TranscriptionResponse)
async def transcribe_audio(
    file: UploadFile = File(...),
    model_size: str = "base",
    language: Optional[str] = "en",
    temperature: float = 0.0,
    prompt: Optional[str] = None
):
    """Transcribe audio file using Whisper v3"""
    try:
        start_time = asyncio.get_event_loop().time()
        
        # Load model if not already loaded
        model = load_whisper_model(model_size)
        
        # Read audio file
        audio_data = await file.read()
        
        # Convert mu-law to WAV if needed
        if file.content_type == "audio/mulaw" or file.filename.endswith('.mulaw'):
            audio_data = convert_mulaw_to_wav(audio_data)
        
        # Create temporary file for Whisper
        temp_file = io.BytesIO(audio_data)
        temp_file.name = "audio.wav"
        
        # Transcribe with Whisper
        result = model.transcribe(
            temp_file,
            language=language,
            temperature=temperature,
            initial_prompt=prompt,
            verbose=False,
            word_timestamps=False  # Disable for better performance
        )
        
        processing_time = asyncio.get_event_loop().time() - start_time
        
        # Extract segments and calculate average log probability
        segments = result.get("segments", [])
        avg_logprob = None
        if segments:
            logprobs = [seg.get("avg_logprob", 0) for seg in segments if seg.get("avg_logprob") is not None]
            if logprobs:
                avg_logprob = sum(logprobs) / len(logprobs)
        
        return TranscriptionResponse(
            text=result["text"].strip(),
            avg_logprob=avg_logprob,
            segments=segments,
            processing_time=processing_time
        )
        
    except Exception as e:
        logger.error(f"Transcription failed: {e}")
        raise HTTPException(status_code=500, detail=f"Transcription failed: {e}")

@app.post("/transcribe-optimized", response_model=TranscriptionResponse)
async def transcribe_optimized(
    file: UploadFile = File(...),
    prompt: Optional[str] = "Caller is speaking about salon services or booking appointments. Focus on clear human speech and maintain natural conversation flow. Ignore background noise, dial tones, and audio artifacts."
):
    """Optimized transcription endpoint for salon phone calls"""
    return await transcribe_audio(
        file=file,
        model_size="base",  # Good balance of speed/accuracy for phone calls
        language="en",
        temperature=0.0,
        prompt=prompt
    )

if __name__ == "__main__":
    # Pre-load model on startup for faster first request
    model_size = os.getenv("WHISPER_MODEL_SIZE", "base")
    load_whisper_model(model_size)
    
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
