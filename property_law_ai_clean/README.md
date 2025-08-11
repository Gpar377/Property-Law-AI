# Property Law AI Assistant

AI-powered legal analysis for Bangalore property disputes using advanced AI technology.

## Features

- 🤖 **AI-Powered Analysis**: Expert legal analysis using GPT-4
- 🏛️ **Karnataka Law Expert**: Specialized in Bangalore property law
- 📄 **Detailed Reports**: Comprehensive PDF reports
- 🔐 **User Authentication**: Secure login and case history
- 📱 **Responsive Design**: Works on all devices

## Tech Stack

**Frontend:**
- HTML5, CSS3, JavaScript (Vanilla)
- Responsive design with modern UI

**Backend:**
- FastAPI (Python)
- OpenAI GPT-4 integration
- JWT authentication
- Supabase PostgreSQL database

## Local Development

### Backend Setup
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
uvicorn main:app --reload --port 8001
```

### Frontend Setup
```bash
cd frontend
python serve.py  # Starts on port 3000
```

### Environment Variables
Create `backend/.env`:
```
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
OPENAI_API_KEY=your_openai_key
SECRET_KEY=your_jwt_secret
```

## Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions.

## Legal Disclaimer

This application is for educational purposes only. Always consult a qualified lawyer for legal advice.

## License

MIT License - see LICENSE file for details.