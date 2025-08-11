# Deployment Guide

## Backend Deployment (Railway/Render)

### Option 1: Railway
1. Go to https://railway.app
2. Connect your GitHub repo
3. Select the `backend` folder
4. Add environment variables:
   - `SUPABASE_URL`: https://bgsewlriojnpjyexcgrj.supabase.co
   - `SUPABASE_KEY`: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJnc2V3bHJpb2pucGp5ZXhjZ3JqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTQ5MjUwMDIsImV4cCI6MjA3MDUwMTAwMn0.Dig-IjfxUZRqlMaQHIZydkwGRnfwuVOA2ROMZz08rHo
   - `OPENAI_API_KEY`: your_openai_api_key_here
   - `SECRET_KEY`: your_super_secret_jwt_key_here_make_it_long_and_random_123456789
   - `ALGORITHM`: HS256
   - `ACCESS_TOKEN_EXPIRE_MINUTES`: 30
5. Deploy!

### Option 2: Render
1. Go to https://render.com
2. Connect GitHub repo
3. Create new Web Service
4. Root directory: `backend`
5. Build command: `pip install -r requirements.txt`
6. Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
7. Add same environment variables as above

## Frontend Deployment (Vercel/Netlify)

### Option 1: Vercel
1. Go to https://vercel.com
2. Import your GitHub repo
3. Root directory: `frontend`
4. Update `script.js` with your backend URL:
   ```javascript
   const API_BASE_URL = 'https://your-backend-url.railway.app';
   ```
5. Deploy!

### Option 2: Netlify
1. Go to https://netlify.com
2. Drag and drop the `frontend` folder
3. Update API_BASE_URL in script.js first
4. Deploy!

## Quick Deploy Steps:
1. **Push to GitHub** (if not already)
2. **Deploy Backend** to Railway/Render
3. **Update frontend** API_BASE_URL with backend URL
4. **Deploy Frontend** to Vercel/Netlify
5. **Test the live app!**

Your app will be live at:
- Frontend: https://your-app.vercel.app
- Backend: https://your-backend.railway.app