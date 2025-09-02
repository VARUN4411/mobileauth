# E-commerce Authentication System

A production-level, OTP-based authentication system for e-commerce applications built with Django.

## 🚀 Features

### Authentication Flow
- **Passwordless Login**: Users can login using mobile number or email
- **OTP Verification**: Secure 6-digit one-time password verification
- **Auto User Creation**: New users are automatically created on first login
- **Profile Completion**: Guided profile setup for new users

### Security Features
- **OTP Expiry**: OTPs expire after 10 minutes
- **Rate Limiting**: Maximum 3 OTP requests per hour per user
- **Session Management**: Secure session handling with IP tracking
- **Attempt Limiting**: Maximum 3 failed OTP attempts per OTP

### User Experience
- **Modern UI**: Beautiful, responsive design with Bootstrap 5
- **Auto-formatting**: Mobile numbers are automatically formatted
- **Auto-submit**: OTP form submits automatically when 6 digits are entered
- **Resend OTP**: Users can request new OTPs with cooldown timer

## 🏗️ Architecture

### Models
- **User**: Custom user model with mobile/email authentication
- **UserProfile**: Extended user information (name, address, etc.)
- **OTP**: One-time password management with expiry and attempts
- **UserSession**: Session tracking for security

### Database Design
```
User (1) ←→ (1) UserProfile
User (1) ←→ (N) OTP
User (1) ←→ (N) UserSession
```

## 🛠️ Installation

### Prerequisites
- Python 3.8+
- pip
- Virtual environment (recommended)

### Setup Steps

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd auth_project
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Create superuser (optional)**
   ```bash
   python manage.py createsuperuser
   ```

6. **Run the development server**
   ```bash
   python manage.py runserver
   ```

7. **Access the application**
   - Main app: http://localhost:8000/
   - Admin panel: http://localhost:8000/admin/

## 📱 Usage

### For Users

1. **Login**
   - Visit the login page
   - Enter mobile number or email
   - Receive OTP via SMS/email
   - Enter 6-digit OTP
   - Complete profile (first-time users)

2. **Profile Management**
   - Edit personal information
   - Update shipping address
   - View account details

### For Developers

1. **Customization**
   - Modify templates in `templates/authapp/`
   - Update forms in `authapp/forms.py`
   - Customize views in `authapp/views.py`

2. **SMS/Email Integration**
   - Update `authapp/utils.py` with your SMS/email service
   - Configure API keys in environment variables

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the project root:

```env
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Email Settings (for OTP delivery)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=your-email@gmail.com

# SMS Settings (optional)
TWILIO_ACCOUNT_SID=your-twilio-sid
TWILIO_AUTH_TOKEN=your-twilio-token
TWILIO_PHONE_NUMBER=your-twilio-number
```

### OTP Settings
Configure OTP behavior in `settings.py`:

```python
# OTP Settings
OTP_EXPIRY_MINUTES = 10
OTP_MAX_ATTEMPTS = 3
OTP_LENGTH = 6
```

## 🚀 Production Deployment

### Security Checklist
- [ ] Set `DEBUG = False`
- [ ] Use strong `SECRET_KEY`
- [ ] Configure `ALLOWED_HOSTS`
- [ ] Enable HTTPS
- [ ] Set `SESSION_COOKIE_SECURE = True`
- [ ] Configure proper database (PostgreSQL recommended)
- [ ] Set up email/SMS services
- [ ] Configure static file serving
- [ ] Set up logging

### Recommended Services
- **SMS**: Twilio, AWS SNS, or local SMS gateway
- **Email**: AWS SES, SendGrid, or SMTP
- **Database**: PostgreSQL
- **Web Server**: Nginx + Gunicorn
- **Hosting**: AWS, DigitalOcean, or Heroku

## 📁 Project Structure

```
auth_project/
├── auth_project/          # Main project settings
│   ├── settings.py       # Django settings
│   ├── urls.py          # Main URL configuration
│   └── wsgi.py          # WSGI configuration
├── authapp/              # Authentication app
│   ├── models.py        # Database models
│   ├── views.py         # View functions
│   ├── forms.py         # Form classes
│   ├── utils.py         # Utility functions
│   ├── admin.py         # Admin interface
│   └── urls.py          # App URL configuration
├── templates/            # HTML templates
│   ├── base.html        # Base template
│   └── authapp/         # App-specific templates
├── static/               # Static files (CSS, JS, images)
├── media/                # User-uploaded files
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

## 🔒 Security Features

### OTP Security
- 6-digit random OTP generation
- 10-minute expiration
- Maximum 3 attempts per OTP
- Rate limiting (3 OTPs per hour per user)

### Session Security
- Secure session cookies
- IP address tracking
- User agent logging
- Session expiry management

### Input Validation
- Mobile number format validation
- Email format validation
- CSRF protection
- XSS prevention

## 🧪 Testing

### Run Tests
```bash
python manage.py test authapp
```

### Test Coverage
```bash
pip install coverage
coverage run --source='.' manage.py test
coverage report
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Contact the development team
- Check the documentation

## 🔮 Future Enhancements

- [ ] Two-factor authentication (2FA)
- [ ] Social login integration
- [ ] Advanced rate limiting
- [ ] Audit logging
- [ ] API endpoints for mobile apps
- [ ] Multi-language support
- [ ] Dark mode theme
- [ ] Advanced analytics

---

**Built with ❤️ using Django and Bootstrap**

