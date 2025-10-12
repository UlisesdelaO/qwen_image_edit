# API Testing Guide

## Build Status
- ✅ **Code Updated**: October 12, 2025
- ✅ **Git Push**: Successful
- ✅ **GitHub Tag**: v1.1.0 created
- 🔄 **RunPod Build**: In progress

## Testing Your API

### 1. Wait for Build Completion
- Check RunPod dashboard for build completion
- Look for "Completed" status in the Builds tab

### 2. Test API with curl
```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -d '{
    "input": {
      "prompt": "Un retrato al estilo de un cómic de los 90s",
      "user_image": "BASE64_IMAGE_STRING"
    }
  }' \
  "https://n33kwiymnomaax.api.runpod.ai/runsync"
```

### 3. Expected Response
```json
{
  "image_base64": "base64_encoded_result_image"
}
```

## Troubleshooting
- If 400 error: Check image format and size
- If timeout: Verify endpoint is running
- If 500 error: Check RunPod logs

## Next Steps
1. Monitor RunPod dashboard
2. Test API once build completes
3. Verify image processing works correctly
