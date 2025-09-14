# Railway Deployment Checklist

## Pre-deployment Setup

### 1. GitHub Repository
- [ ] Push all code to GitHub repository
- [ ] Ensure all files are committed including:
  - [ ] `Procfile`
  - [ ] `nixpacks.toml`
  - [ ] `requirements.txt`
  - [ ] All Python files and templates

### 2. Environment Variables
Set these in Railway dashboard:

```env
# Required - Database (Railway provides automatically)
DATABASE_URL=postgresql://...

# Required - Flask Security
NEXTAUTH_SECRET=your-secure-random-string-here

# Required - Email Configuration
GMAIL_USER=your-email@gmail.com
GMAIL_APP_PASSWORD=your-gmail-app-password

# Required - Stripe Configuration
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Optional - Akahu Integration
AKAHU_APP_TOKEN=your-akahu-app-token
AKAHU_USER_TOKEN=your-akahu-user-token
```

### 3. External Service Setup

#### Gmail App Password
1. Enable 2-factor authentication on Gmail
2. Go to Google Account → Security → 2-Step Verification → App passwords
3. Generate password for "Mail"
4. Use this password in `GMAIL_APP_PASSWORD`

#### Stripe Configuration
1. Create Stripe account at https://stripe.com
2. Get API keys from dashboard
3. Create webhook endpoint: `https://your-app.up.railway.app/subscription/webhook`
4. Configure webhook events:
   - `customer.subscription.created`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
   - `invoice.payment_succeeded`
   - `invoice.payment_failed`

## Railway Deployment Steps

### 1. Connect Repository
- [ ] Login to Railway dashboard
- [ ] Click "New Project"
- [ ] Select "Deploy from GitHub repo"
- [ ] Choose your repository

### 2. Configure Environment Variables
- [ ] Go to project settings
- [ ] Add all environment variables listed above
- [ ] Railway will auto-provide `DATABASE_URL`

### 3. Deploy Application
- [ ] Railway will automatically build and deploy
- [ ] Monitor build logs for any errors
- [ ] Verify application starts successfully

### 4. Post-Deployment Configuration

#### Update Stripe Webhook URL
- [ ] Copy your Railway app URL (e.g., `https://rent4-production-1234.up.railway.app`)
- [ ] Update Stripe webhook URL to: `https://your-app.up.railway.app/subscription/webhook`

#### Test Application Features
- [ ] Visit your app URL
- [ ] Test user registration and email verification
- [ ] Test login/logout
- [ ] Test property addition (should be limited to 1)
- [ ] Test Stripe upgrade flow
- [ ] Test bank integration page

## Troubleshooting

### Common Issues

1. **Build fails with Python errors**
   - Check `requirements.txt` for version conflicts
   - Verify all Python files have correct syntax

2. **Database connection errors**
   - Ensure `DATABASE_URL` is set (Railway provides this)
   - Check database migrations ran successfully

3. **Email not working**
   - Verify `GMAIL_USER` and `GMAIL_APP_PASSWORD` are correct
   - Check Gmail app password is generated correctly

4. **Stripe webhooks failing**
   - Verify webhook URL is correct
   - Check `STRIPE_WEBHOOK_SECRET` matches Stripe dashboard
   - Ensure webhook events are configured correctly

### Monitoring

- [ ] Check Railway application logs
- [ ] Monitor Stripe webhook delivery in dashboard
- [ ] Test email delivery manually
- [ ] Verify database tables were created

## Production Readiness

The application includes:
- ✅ Production-ready Flask configuration
- ✅ Gunicorn WSGI server
- ✅ PostgreSQL database support
- ✅ Environment variable configuration
- ✅ Error handling and logging
- ✅ Security features (CSRF, rate limiting)
- ✅ Responsive web design
- ✅ Email verification system
- ✅ Payment processing with Stripe
- ✅ Bank integration support

## Post-Launch Tasks

1. **Monitor Usage**
   - Track user registrations
   - Monitor payment processing
   - Check email delivery rates

2. **Implement Akahu Integration**
   - Complete bank transaction fetching
   - Test with real bank accounts
   - Add transaction search functionality

3. **Enhanced Features**
   - Payment history analytics
   - Tenant management features
   - Advanced reporting
   - Mobile app support

## Support

For deployment issues:
- Check Railway documentation
- Review application logs
- Test locally with PostgreSQL database
- Verify all environment variables are set correctly