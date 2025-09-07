# Supabase Setup Guide

This guide will help you set up a Supabase project for the YouTube Productivity application.

## Prerequisites

- A Supabase account ([sign up here](https://supabase.com))
- Node.js 18+ (for local development)
- Supabase CLI (optional, for local development)

## Step 1: Create a Supabase Project

1. Go to [Supabase Dashboard](https://app.supabase.com)
2. Click "New Project"
3. Choose your organization
4. Fill in project details:
   - **Name**: `youtube-productivity` (or your preferred name)
   - **Database Password**: Generate a strong password and save it
   - **Region**: Choose the region closest to your users
5. Click "Create new project"
6. Wait for the project to be created (usually takes 1-2 minutes)

## Step 2: Get Project Credentials

1. In your project dashboard, go to **Settings** → **API**
2. Copy the following values:
   - **Project URL**
   - **anon public** key
   - **service_role** key (keep this secret!)

## Step 3: Create Storage Bucket

1. In your project dashboard, go to **Storage**
2. Click "Create a new bucket"
3. **Bucket name**: Use the value from your `SUPABASE_BUCKET` environment variable
   - If not set, use: `youtube-productivity-files`
4. **Public bucket**: ✅ Check this (for public access to thumbnails, etc.)
5. Click "Create bucket"

## Step 4: Run Database Schema

### Option A: Using Supabase Dashboard (Recommended for beginners)

1. Go to **SQL Editor** in your Supabase dashboard
2. Click "New query"
3. Copy the contents of `schema.sql` and paste it into the editor
4. Click "Run" to execute the schema

### Option B: Using Supabase CLI (For developers)

1. Install Supabase CLI:
   ```bash
   npm install -g supabase
   ```

2. Login to Supabase:
   ```bash
   supabase login
   ```

3. Link your project:
   ```bash
   supabase link --project-ref YOUR_PROJECT_REF
   ```

4. Run the migration:
   ```bash
   supabase db push
   ```

### Option C: Using psql (Advanced)

1. Get your database connection string from **Settings** → **Database**
2. Run the schema file:
   ```bash
   psql "postgresql://postgres:[YOUR-PASSWORD]@db.[YOUR-PROJECT-REF].supabase.co:5432/postgres" -f schema.sql
   ```

## Step 5: Environment Variables

Create a `.env` file in your project root with the following variables:

```env
# Supabase Configuration
SUPABASE_URL=https://[YOUR-PROJECT-REF].supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InN1eWV5cGxhZG56ZGJiZnB1b2V3Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTcyMjI1MjMsImV4cCI6MjA3Mjc5ODUyM30.NSj4ykYyk-xhHqTp9bpznJWRMmbp1zB3F_Vi9pgwXlU
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InN1eWV5cGxhZG56ZGJiZnB1b2V3Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NzIyMjUyMywiZXhwIjoyMDcyNzk4NTIzfQ.OoVLUdVYcXdELOBQHsoo-0TpWhfGmlRCmPFCd468J34
SUPABASE_BUCKET=youtube-productivity-files

# Optional: For local development
SUPABASE_DB_PASSWORD=[YOUR-DATABASE-PASSWORD]
```

**Important**: 
- Replace `[YOUR-PROJECT-REF]` with your actual project reference
- Replace `[YOUR-ANON-KEY]` with your anon public key
- Replace `[YOUR-SERVICE-ROLE-KEY]` with your service role key
- Replace `[YOUR-DATABASE-PASSWORD]` with your database password

## Step 6: Verify Setup

1. Go to **Table Editor** in your Supabase dashboard
2. You should see the following tables:
   - `users`
   - `videos`
   - `transcripts`
   - `summaries`
   - `jobs`

3. Check that sample data was inserted in the `users` table

## Step 7: Configure Row Level Security (RLS)

For production, you should enable Row Level Security:

1. Go to **Authentication** → **Policies**
2. Enable RLS on all tables
3. Create policies based on your application's needs

Example policy for users table:
```sql
-- Users can only see their own data
CREATE POLICY "Users can view own profile" ON users
    FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can update own profile" ON users
    FOR UPDATE USING (auth.uid() = id);
```

## Local Development (Optional)

If you want to run Supabase locally:

1. Install Supabase CLI
2. Initialize Supabase in your project:
   ```bash
   supabase init
   ```
3. Start local Supabase:
   ```bash
   supabase start
   ```
4. Run migrations:
   ```bash
   supabase db reset
   ```

## Troubleshooting

### Common Issues:

1. **"relation does not exist"**: Make sure you ran the schema.sql file
2. **"permission denied"**: Check your API keys and RLS policies
3. **"bucket not found"**: Verify the bucket name matches your environment variable

### Getting Help:

- [Supabase Documentation](https://supabase.com/docs)
- [Supabase Discord](https://discord.supabase.com)
- [GitHub Issues](https://github.com/supabase/supabase/issues)

## Next Steps

After setting up the database:

1. Configure your backend to connect to Supabase
2. Set up authentication (if needed)
3. Implement video processing workflows
4. Test the API endpoints

Your Supabase project is now ready for the YouTube Productivity application! 🚀
