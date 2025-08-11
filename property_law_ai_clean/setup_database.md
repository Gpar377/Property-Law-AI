# Database Setup Instructions

## Step 1: Access Supabase Dashboard
1. Go to https://supabase.com
2. Sign in to your account
3. Select your project

## Step 2: Run SQL Script
1. Click on "SQL Editor" in the left sidebar
2. Click "New Query"
3. Copy and paste the entire content from `database_setup.sql`
4. Click "Run" to execute the script

## Step 3: Verify Tables Created
1. Go to "Table Editor" in the left sidebar
2. You should see three tables:
   - `users`
   - `cases` 
   - `case_documents`

## Step 4: Test the Application
1. Both servers should be running:
   - Backend: http://localhost:8000
   - Frontend: http://localhost:3000
2. Try registering a new user
3. Submit a test case for analysis

## Troubleshooting
- If you get "table not found" errors, make sure you ran the SQL script
- Check that your Supabase URL and API key are correct in the `.env` file
- Ensure both servers are running on different ports (3000 and 8000)