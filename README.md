# Whisper v3 Transcription Service

A lightweight FastAPI service for running OpenAI Whisper v3 models, optimized for Heroku deployment and phone call transcription.

## Features

- **Whisper v3 Support**: Latest model with improved accuracy
- **Heroku Optimized**: Memory-efficient with CPU-only inference
- **Phone Call Optimized**: Specialized for mu-law audio from Twilio
- **Multiple Model Sizes**: tiny, base, small, medium, large-v3
- **FastAPI**: Modern async API with automatic documentation

## Deployment to Heroku

### Option 1: Heroku CLI
```bash
# Create new Heroku app
heroku create your-whisper-service

# Set environment variables
heroku config:set WHISPER_MODEL_SIZE=base

# Deploy
git add .
git commit -m "Initial Whisper service"
git push heroku main
```

### Option 2: Heroku Dashboard
1. Create new app in Heroku dashboard
2. Connect to your GitHub repository
3. Set environment variables:
   - `WHISPER_MODEL_SIZE=base` (or tiny/small/medium/large-v3)
4. Deploy from main branch

## Model Size Recommendations

| Model | Size | Memory | Speed | Accuracy | Use Case |
|-------|------|--------|-------|----------|----------|
| tiny | 39MB | ~1GB | Fastest | Good | Development/Testing |
| base | 74MB | ~1GB | Fast | Better | **Recommended for phone calls** |
| small | 244MB | ~2GB | Medium | Good | High accuracy needs |
| medium | 769MB | ~5GB | Slow | Better | Not recommended for Heroku |
| large-v3 | 1550MB | ~10GB | Slowest | Best | Not recommended for Heroku |

## API Endpoints

### Health Check
```
GET /health
```

### Standard Transcription
```
POST /transcribe
- file: Audio file (WAV, MP3, M4A, etc.)
- model_size: tiny|base|small|medium|large-v3
- language: en (optional)
- temperature: 0.0 (optional)
- prompt: Custom prompt (optional)
```

### Optimized for Phone Calls
```
POST /transcribe-optimized
- file: Audio file (supports mu-law from Twilio)
- prompt: Salon-specific prompt (optional)
```

## Usage in Your Main App

Set the environment variable in your main app:
```bash
REMOTE_WHISPER_URL=https://your-whisper-service.herokuapp.com
```

The existing code will automatically use the remote service when this is set.

## Cost Estimation

### Heroku Dyno Costs
- **Basic ($7/month)**: 512MB RAM - Only supports `tiny` model
- **Standard-1X ($25/month)**: 512MB RAM - Supports `base` model
- **Standard-2X ($50/month)**: 1GB RAM - Supports `small` model
- **Performance-M ($250/month)**: 2.5GB RAM - Supports `medium` model

### Recommended Setup
- **Model**: `base` (good balance of speed/accuracy)
- **Dyno**: Standard-1X ($25/month)
- **Total Cost**: ~$25/month for dedicated transcription service

## Performance

- **Base Model**: ~2-3 seconds per 10 seconds of audio
- **Memory Usage**: ~1GB RAM
- **Concurrent Requests**: 1-2 (due to memory constraints)

## Troubleshooting

### Out of Memory Errors
- Use smaller model (`tiny` or `base`)
- Upgrade to larger dyno
- Implement request queuing

### Slow Performance
- Use `tiny` model for faster transcription
- Implement caching for repeated audio
- Consider upgrading dyno type

### Model Loading Issues
- Models are downloaded to `/tmp` on Heroku
- First request may be slow due to model download
- Consider pre-warming the service
