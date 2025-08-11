# 🚀 Property Law AI Assistant - Quick Setup Guide

## Step 1: Run Setup Script
Double-click `setup.bat` to install all dependencies automatically.

## Step 2: Get Your API Keys

### 🔑 OpenAI API Key
1. Go to [OpenAI Platform](https://platform.openai.com/api-keys)
2. Sign up/Login
3. Click "Create new secret key"
4. Copy the key (starts with `sk-`)

### 🗄️ Supabase Database
1. Go to [Supabase](https://supabase.com)
2. Sign up/Login
3. Click "New Project"
4. Choose organization and create project
5. Wait for setup to complete
6. Go to Settings → API
7. Copy:
   - Project URL
   - Anon/Public key

## Step 3: Configure Environment
1. Open `backend\.env` file
2. Replace the placeholder values:
   ```
   SUPABASE_URL=https://your-project-id.supabase.co
   SUPABASE_KEY=your_supabase_anon_key
   OPENAI_API_KEY=sk-your_openai_key
   ```

## Step 4: Setup Database
1. Go to your Supabase project
2. Click "SQL Editor" in the sidebar
3. Copy and paste the contents of `database_setup.sql`
4. Click "Run" to create tables

## Step 5: Start the Application

### Option A: Start Both (Recommended)
1. Double-click `start.bat` (starts backend)
2. Double-click `start_frontend.bat` (starts frontend)

### Option B: Manual Start
1. Backend: `cd backend && venv\Scripts\activate && uvicorn main:app --reload`
2. Frontend: `cd frontend && python serve.py`

## 🌐 Access the Application
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## 🧪 Test the Application
1. Open http://localhost:3000
2. Click "Register" to create an account
3. Login with your credentials
4. Click "Analyze Case" and try a sample case:
   ```
   Title: Property Inheritance Dispute
   Type: Inheritance & Partition
   Details: My father passed away leaving a property in Bangalore. 
   There are 3 legal heirs - myself and my two brothers. The property 
   is currently in my father's name and we want to partition it equally. 
   What are the legal steps required?
   ```

## 🔧 Troubleshooting

### Backend Issues
- **Port 8000 in use**: Change port in `start.bat`
- **Module not found**: Run `setup.bat` again
- **Database errors**: Check Supabase credentials in `.env`

### Frontend Issues
- **Port 3000 in use**: Change PORT in `frontend/serve.py`
- **API connection failed**: Make sure backend is running

### API Key Issues
- **OpenAI errors**: Verify API key and billing setup
- **Supabase errors**: Check project URL and anon key

## 📝 Sample Test Cases

### Boundary Dispute
```
Title: Neighbor Encroachment Issue
Type: Boundary Disputes
Details: My neighbor has constructed a wall that extends 2 feet into my property. I have the original survey documents and property registration papers. The encroachment has been there for about 6 months. What legal action can I take?
```

### BBMP Issue
```
Title: Building Plan Approval Delay
Type: BBMP/BDA Issues
Details: I applied for building plan approval with BBMP 8 months ago for a residential construction in Koramangala. Despite submitting all required documents, there has been no response. What are my options to expedite this process?
```

## 🎯 Next Steps
Once everything is working:
1. Customize the AI prompts in `backend/ai_service.py`
2. Modify the UI in `frontend/` files
3. Deploy to production using the deployment guides

## 🆘 Need Help?
If you encounter any issues:
1. Check the console/terminal for error messages
2. Verify all API keys are correct
3. Make sure both servers are running
4. Check the troubleshooting section above

Happy analyzing! 🏠⚖️