# Django Superuser Setup for Railway Deployment

## Overview
A Django management command has been created to automatically set up a superuser during Railway deployment.

## Environment Variables

Set these environment variables in your Railway project dashboard:

### Required Variables
```
DJANGO_SUPERUSER_USERNAME=your_admin_username
DJANGO_SUPERUSER_EMAIL=your_admin_email@example.com  
DJANGO_SUPERUSER_PASSWORD=your_secure_password_here
```

### Default Values (if variables not set)
- **Username**: `admin`
- **Email**: `admin@example.com`
- **Password**: `admin123` ⚠️ **Change this immediately!**

## Setting Environment Variables in Railway

1. Go to your Railway project dashboard
2. Navigate to the **Variables** tab
3. Add the following environment variables:
   - `DJANGO_SUPERUSER_USERNAME`
   - `DJANGO_SUPERUSER_EMAIL` 
   - `DJANGO_SUPERUSER_PASSWORD`

## Security Recommendations

🔐 **Important Security Notes:**

1. **Use a strong password** - Include uppercase, lowercase, numbers, and special characters
2. **Use a real email address** - This will be your admin account
3. **Choose a unique username** - Don't use common names like "admin" in production

### Example Strong Setup
```
DJANGO_SUPERUSER_USERNAME=mycompany_admin
DJANGO_SUPERUSER_EMAIL=admin@yourcompany.com
DJANGO_SUPERUSER_PASSWORD=MyStr0ng!P@ssw0rd2024
```

## How It Works

- The command runs automatically during Railway's release phase
- If a superuser already exists, it skips creation (safe to run multiple times)
- The superuser is created before the web application starts
- You can access the admin panel at: `https://your-app.up.railway.app/admin/`

## Manual Creation (Alternative)

If you prefer to create the superuser manually:

1. Open Railway's project dashboard
2. Go to **Deployments** tab  
3. Click on a running deployment
4. Open the **Terminal** tab
5. Run: `python manage.py createsuperuser`

## Troubleshooting

### Command Not Found
If you get a "command not found" error, ensure:
- The `stories/management/commands/create_superuser.py` file exists
- The `__init__.py` files exist in both management directories
- The app has been deployed with the latest changes

### Superuser Not Created
Check the deployment logs for error messages. Common issues:
- Invalid email format
- Password doesn't meet Django's requirements
- Database connection issues

## Testing Locally

To test the command locally:
```bash
python manage.py create_superuser
```

If a superuser exists, you'll see: "Superuser already exists. Skipping creation." 