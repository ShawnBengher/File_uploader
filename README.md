## Challenge 1: Simple File Uploader (Python + FastAPI + AWS S3)

### Backend
- Stack: FastAPI, Uvicorn, Boto3, python-multipart
- Endpoints:
  - GET `/health`
  - POST `/upload` (form-data `file`) -> returns presigned URL (1h)
- Validation: MIME type allowlist, size limit (default 5 MB), S3 metadata logging

### Frontend
- Static `frontend/index.html` with a simple upload form
- Enter backend URL (e.g., `http://127.0.0.1:8000`) and upload

### Setup
1) Install Python 3.10+ and AWS credentials with access to S3 bucket
2) Create `.env` in `backend/` based on `.env.example`
3) Create venv and install deps:
```powershell
cd backend
py -3 -m venv .venv
. .venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Run
```powershell
cd backend
. .venv\Scripts\Activate.ps1
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```
Open `frontend/index.html` in a browser (or use a local server) and set Backend URL to `http://127.0.0.1:8000`.

### AWS S3 Policy (example)
Grant the user/programmatic credentials at least PutObject and GetObject on the bucket.

### Deploy to Vercel (Backend + Frontend)

**Prerequisites:**
1. Install Vercel CLI: `npm i -g vercel`
2. Create AWS S3 bucket and get access keys
3. Login to Vercel: `vercel login`

**Deploy Backend:**
1. Set environment variables:
   ```bash
   vercel env add AWS_ACCESS_KEY_ID
   vercel env add AWS_SECRET_ACCESS_KEY  
   vercel env add S3_BUCKET_NAME
   vercel env add AWS_REGION
   vercel env add ALLOWED_ORIGINS
   ```
2. Deploy: `vercel --prod`
3. Get your backend URL (e.g., `https://your-app.vercel.app`)

**Deploy Frontend:**
1. In Vercel dashboard, create new project
2. Connect your GitHub repo
3. Set build command: `echo 'Static site'`
4. Set output directory: `frontend`
5. Deploy

**Live Demo:**
- Backend API: `https://your-app.vercel.app`
- Frontend: `https://your-frontend.vercel.app`
- Health check: `https://your-app.vercel.app/health`

### Environment Variables
See `backend/.env.example`.



