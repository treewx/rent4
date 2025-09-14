# Rent4 - Automated Rent Tracking

A web-based application that automatically tracks rent payments by monitoring bank statements and sends notifications to landlords when rent is received or missed.

## Features

- **User Authentication**: Email verification, password reset, secure login
- **Property Management**: Add, edit, and delete rental properties
- **Bank Integration**: Secure connection with Akahu for transaction monitoring
- **Automated Rent Tracking**: Daily checks for rent payments
- **Email Notifications**: Automatic alerts for received, missed, or partial payments
- **Tenant Reminders**: Optional automated emails to tenants when rent is missed
- **Subscription Management**: Free (1 property) and Premium (unlimited) plans via Stripe

## Tech Stack

- **Backend**: Flask (Python)
- **Database**: PostgreSQL
- **Frontend**: Bootstrap 5, Jinja2 templates
- **Email**: Gmail SMTP
- **Payments**: Stripe
- **Bank Integration**: Akahu API
- **Deployment**: Railway

## Setup Instructions

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd rent4
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Environment Variables

Copy the example environment file and configure your variables:

```bash
cp .env.example .env
```

Edit `.env` with your actual values:

```env
# Flask Configuration
FLASK_ENV=development
NEXTAUTH_SECRET=your-secret-key-here

# Database Configuration
DATABASE_URL=postgresql://username:password@localhost:5432/rent4

# Gmail Configuration
GMAIL_USER=your-email@gmail.com
GMAIL_APP_PASSWORD=your-gmail-app-password

# Stripe Configuration
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
```

### 4. Database Setup

Make sure you have PostgreSQL installed and create a database:

```sql
CREATE DATABASE rent4;
```

The application will automatically create the necessary tables on first run.

### 5. Gmail Setup

1. Enable 2-factor authentication on your Gmail account
2. Generate an App Password:
   - Go to Google Account settings
   - Security → 2-Step Verification → App passwords
   - Generate a new app password for "Mail"
   - Use this password in `GMAIL_APP_PASSWORD`

### 6. Stripe Setup

1. Create a Stripe account at https://stripe.com
2. Get your API keys from the Stripe dashboard
3. Set up a webhook endpoint pointing to: `your-domain.com/subscription/webhook`
4. Configure the webhook to listen for:
   - `customer.subscription.created`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
   - `invoice.payment_succeeded`
   - `invoice.payment_failed`

### 7. Run the Application

```bash
python app.py
```

The application will be available at `http://localhost:5000`

## Deployment to Railway

### 1. Prepare for Deployment

The application is already configured for Railway deployment with:
- `Procfile` for gunicorn
- `nixpacks.toml` for build configuration
- Environment variable handling

### 2. Deploy to Railway

1. Connect your GitHub repository to Railway
2. Set the environment variables in Railway dashboard:
   - `DATABASE_URL` (automatically provided by Railway)
   - `GMAIL_USER`
   - `GMAIL_APP_PASSWORD`
   - `STRIPE_PUBLISHABLE_KEY`
   - `STRIPE_SECRET_KEY`
   - `STRIPE_WEBHOOK_SECRET`
   - `NEXTAUTH_SECRET`

3. Railway will automatically deploy your application

### 3. Update Stripe Webhook URL

After deployment, update your Stripe webhook URL to:
`https://your-app-name.up.railway.app/subscription/webhook`

## Usage

### For Landlords

1. **Register**: Create an account with email verification
2. **Set up Bank Integration**: Connect your bank account via Akahu
3. **Add Properties**: Enter property details including:
   - Property address
   - Tenant information
   - Rent amount and frequency
   - Bank statement keyword for identification
4. **Automatic Tracking**: The system checks for rent payments daily
5. **Receive Notifications**: Get email alerts for received, missed, or partial payments

### For Tenants

- Receive automated reminder emails when rent payments are missed (if enabled by landlord)

## Payment Plans

- **Free Plan**: 1 property, basic notifications
- **Premium Plan**: $10/month NZD, unlimited properties, tenant reminders, advanced features

## API Integration

### Akahu Bank Integration

The application uses Akahu's open banking API to securely access bank transaction data. Users need to:

1. Create an Akahu account at https://akahu.nz
2. Get their App Token and User Token
3. Enter these tokens in the Bank Integration page

## Security Features

- Password hashing with Werkzeug
- Email verification required for account activation
- Rate limiting on authentication endpoints
- CSRF protection on all forms
- Secure token generation for password resets
- Encrypted storage of sensitive data

## Development

### Running in Development Mode

```bash
export FLASK_ENV=development
python app.py
```

In development mode:
- Scheduler is disabled
- Email verification is auto-completed
- Detailed logging is enabled

### Testing

The application includes basic error handling and logging. For comprehensive testing:

1. Test email flows with actual Gmail credentials
2. Test Stripe integration with test keys
3. Verify database operations work correctly
4. Test the payment checking logic

## Support

For issues or questions:
- Check the application logs
- Verify environment variables are set correctly
- Ensure database connection is working
- Test email configuration separately

## License

This project is licensed under the MIT License.