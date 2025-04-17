# MentiBot - Mental Health Support Platform (Django Version)

MentiBot is a comprehensive mental health support platform built with Django, designed to help users track their mood, manage stress, and receive mental health support through an AI chatbot companion.

## Features

- **User Authentication**: Secure user registration and login system
- **Mood Tracking**: Track and visualize your emotional well-being over time
- **AI Chatbot**: 24/7 emotional support and guidance
- **Stress Management**: Access meditation audio and breathing exercises
- **Data Export**: Export your mood tracking data for personal analysis
- **Responsive Design**: Modern, mobile-friendly interface using Tailwind CSS

## Tech Stack

- Django 4.2.7
- Python 3.8+
- SQLite Database
- Tailwind CSS
- Chart.js for data visualization
- Font Awesome icons

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/django-mentibot.git
cd django-mentibot
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Apply database migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

5. Create a superuser (admin):
```bash
python manage.py createsuperuser
```

6. Run the development server:
```bash
python manage.py runserver
```

7. Visit http://localhost:8000 in your browser

## Project Structure

```
django_mentibot/
├── mentibot/              # Project settings
├── accounts/             # User authentication app
├── mood/                 # Mood tracking app
├── chatbot/             # AI chatbot app
├── stress/              # Stress management app
├── templates/           # HTML templates
│   ├── base.html
│   ├── index.html
│   ├── registration/
│   ├── mood/
│   ├── chatbot/
│   └── stress/
├── static/              # Static files (CSS, JS)
├── media/              # User-uploaded files
└── requirements.txt    # Project dependencies
```

## Features in Detail

### Mood Tracking
- Record daily mood entries with optional notes
- Visualize mood patterns over time using Chart.js
- Export mood data to CSV format

### AI Chatbot
- 24/7 emotional support and guidance
- Quick response suggestions
- Context-aware conversations

### Stress Management
- Guided breathing exercises
- Meditation audio tracks
- Mindfulness resources and tips

## Security

- User authentication required for all features
- Password hashing using Django's security features
- CSRF protection
- Secure session handling

## Contributing

1. Fork the repository
2. Create a new branch (`git checkout -b feature/improvement`)
3. Make your changes
4. Commit your changes (`git commit -am 'Add new feature'`)
5. Push to the branch (`git push origin feature/improvement`)
6. Create a Pull Request

## Important Notice

MentiBot is designed to provide support and guidance but is not a substitute for professional mental health care. If you're experiencing a crisis or need immediate help, please contact emergency services or a mental health professional.

Emergency Contacts:
- Emergency Services: 911
- Crisis Helpline: 988
- National Suicide Prevention Lifeline: 1-800-273-8255

## License

This project is licensed under the MIT License - see the LICENSE file for details.
