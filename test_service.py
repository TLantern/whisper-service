#!/usr/bin/env python3
"""
Test script for Whisper v3 service
"""

import asyncio
import httpx
import os
import wave
import io

async def test_whisper_service(base_url: str):
    """Test the Whisper service endpoints"""
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        print(f"🧪 Testing Whisper service at: {base_url}")
        
        # Test health endpoint
        print("\n1. Testing health endpoint...")
        try:
            response = await client.get(f"{base_url}/health")
            if response.status_code == 200:
                print("✅ Health check passed")
                print(f"   Response: {response.json()}")
            else:
                print(f"❌ Health check failed: {response.status_code}")
                return
        except Exception as e:
            print(f"❌ Health check error: {e}")
            return
        
        # Test transcription with sample audio
        print("\n2. Testing transcription endpoint...")
        
        # Create a simple test audio file (1 second of silence)
        sample_rate = 8000
        duration = 1.0
        num_samples = int(sample_rate * duration)
        
        # Generate silence (all zeros)
        audio_data = b'\x00' * (num_samples * 2)  # 16-bit samples
        
        # Create WAV file
        wav_buffer = io.BytesIO()
        with wave.open(wav_buffer, 'wb') as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(audio_data)
        
        wav_data = wav_buffer.getvalue()
        
        # Test transcription
        try:
            files = {"file": ("test_audio.wav", wav_data, "audio/wav")}
            response = await client.post(f"{base_url}/transcribe-optimized", files=files)
            
            if response.status_code == 200:
                result = response.json()
                print("✅ Transcription test passed")
                print(f"   Text: '{result['text']}'")
                print(f"   Processing time: {result['processing_time']:.2f}s")
                print(f"   Avg logprob: {result.get('avg_logprob', 'N/A')}")
            else:
                print(f"❌ Transcription test failed: {response.status_code}")
                print(f"   Response: {response.text}")
        except Exception as e:
            print(f"❌ Transcription test error: {e}")
        
        # Test API documentation
        print("\n3. Testing API documentation...")
        try:
            response = await client.get(f"{base_url}/docs")
            if response.status_code == 200:
                print("✅ API documentation accessible")
            else:
                print(f"❌ API documentation not accessible: {response.status_code}")
        except Exception as e:
            print(f"❌ API documentation error: {e}")

async def main():
    """Main test function"""
    base_url = os.getenv("WHISPER_SERVICE_URL", "http://localhost:8000")
    
    if base_url == "http://localhost:8000":
        print("🔧 Testing local service. Make sure to run: python app.py")
    
    await test_whisper_service(base_url)

if __name__ == "__main__":
    asyncio.run(main())
