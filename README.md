# �� AI Story Generator

A powerful, feature-rich web application that generates creative stories using Google Gemini AI with intelligent fallback capabilities. Built with Django and modern web technologies.

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![Django](https://img.shields.io/badge/Django-4.2+-green.svg)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-purple.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## ✨ Features

### 🤖 AI-Powered Story Generation
- **Google Gemini Integration**: Advanced AI story generation with professional prompt engineering
- **Smart Fallback System**: Seamless operation even without AI configured
- **Customizable Parameters**: Genre, length, tone, and keyword-based generation
- **Real-time Status**: Live AI availability indicators

### 📚 Story Management
- **Personal Library**: Complete story history with powerful search and filtering
- **Advanced Search**: Real-time text search with debounced input
- **Multi-dimensional Filtering**: By genre, length, tone, AI vs template, ratings, dates
- **Smart Sorting**: Multiple sorting options including word count and ratings
- **Story Collections**: Organize stories into themed collections with custom colors and icons

### 📥 Export & Sharing
- **Professional PDF Export**: Beautiful formatted PDFs with ReportLab styling
- **Multiple Formats**: TXT, HTML, and PDF exports with metadata
- **Bulk Operations**: ZIP archives for multiple stories and collections
- **Collection Analytics**: Comprehensive statistics and genre distribution

### 👤 User Experience
- **User Authentication**: Secure registration and login system
- **Personal Profiles**: Customizable preferences and statistics tracking
- **Public Gallery**: Discover and share stories with the community
- **Responsive Design**: Beautiful Bootstrap UI that works on all devices

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- pip (Python package manager)
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/rezashariatmadar/story-generator.git
   cd story-generator
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Environment setup**
   ```bash
   cp .env.example .env
   # Edit .env file with your settings
   ```

4. **Database setup**
   ```bash
   python manage.py migrate
   python manage.py createsuperuser  # Optional: Create admin user
   ```

5. **Run the server**
   ```bash
   python manage.py runserver
   ```

6. **Access the application**
   - Open your browser to `http://localhost:8000`
   - Start generating amazing stories!

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the root directory:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Google Gemini AI configuration
GEMINI_API_KEY=your-gemini-api-key-here

# Database configuration (optional)
# DATABASE_URL=postgresql://user:password@localhost:5432/story_generator

# Email configuration (optional)
# EMAIL_HOST=smtp.gmail.com
# EMAIL_PORT=587
# EMAIL_USE_TLS=True
# EMAIL_HOST_USER=your-email@gmail.com
# EMAIL_HOST_PASSWORD=your-app-password
```

### Google Gemini API Setup

1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Add it to your `.env` file as `GEMINI_API_KEY`

**Note**: The application works perfectly without AI configuration using the built-in template system.

## 📖 Usage Guide

### Generating Stories

1. **Navigate to Generate Story**
   - Click "Generate Story" in the navigation
   - Fill in your keywords (e.g., "dragon, castle, magic")
   - Select genre, length, and tone
   - Click "Generate Story"

2. **AI vs Template Generation**
   - 🤖 **AI Mode**: Uses Google Gemini for creative, unique stories
   - 🔧 **Template Mode**: Uses built-in algorithm as fallback
   - Status indicators show which mode is active

### Managing Your Stories

1. **View Your Stories**
   - Go to "My Stories" to see all your generated stories
   - Use the search bar for instant text search
   - Apply filters for genre, length, favorites, etc.

2. **Organize with Collections**
   - Create themed collections (Fantasy, Romance, etc.)
   - Customize with colors and icons
   - View collection statistics and analytics

### Exporting Stories

1. **Individual Export**
   - Open any story detail page
   - Use the Export dropdown to choose format (PDF, TXT, HTML)
   - Download starts automatically

2. **Bulk Export**
   - In "My Stories", use bulk selection mode
   - Select multiple stories
   - Choose export format
   - Download as ZIP archive

## 🏗️ Architecture

### Technology Stack
- **Backend**: Django 4.2+ with Python 3.9+
- **Database**: SQLite (development) / PostgreSQL (production ready)
- **Frontend**: Bootstrap 5.3, JavaScript ES6+
- **AI Integration**: Google Gemini API
- **Export**: ReportLab (PDF), WeasyPrint
- **Authentication**: Django's built-in auth system

### Project Structure
```
story-generator/
├── story_generator/          # Django project settings
├── stories/                  # Main stories app
│   ├── models.py            # Story and Collection models
│   ├── views.py             # Web views and logic
│   ├── ai_service.py        # AI integration service
│   ├── export_service.py    # Export functionality
│   └── ...
├── api/                      # REST API app
├── users/                    # User management app
├── templates/                # HTML templates
├── static/                   # CSS, JS, images
└── requirements.txt          # Python dependencies
```

## 🧪 Development

### Running Tests
```bash
python manage.py test
```

### Creating Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### Admin Interface
```bash
python manage.py createsuperuser
# Access at http://localhost:8000/admin/
```

## 📊 API Documentation

### Story Generation
```http
POST /api/generate/
Content-Type: application/json

{
    "keywords": "dragon, castle, magic",
    "genre": "fantasy",
    "length": "short",
    "tone": "dramatic"
}
```

### Export Story
```http
GET /api/stories/{id}/export/{format}/
```

### Collection Management
```http
GET /api/stories/           # List stories
POST /api/export/multiple/  # Bulk export
GET /api/ai-status/         # Check AI availability
```

## 🎯 Roadmap

### ✅ Phase 1 (MVP) - Completed
- ✅ Basic story generation with keywords
- ✅ Simple web interface
- ✅ User registration/login
- ✅ Story history

### ✅ Phase 2 (Enhanced) - Completed
- ✅ Genre/length/tone selection
- ✅ Story rating system
- ✅ Export functionality (PDF, TXT, HTML)
- ✅ Advanced search and filtering
- ✅ Story collections and organization
- ✅ REST API endpoints

### 🚧 Phase 3 (Advanced) - Upcoming
- 🔄 Social features (sharing, following)
- 🔄 Advanced customization (themes, templates)
- 🔄 Analytics dashboard
- 🔄 Mobile app responsiveness
- 🔄 Performance optimizations

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Google Gemini AI](https://ai.google.dev/) for powerful story generation
- [Django](https://www.djangoproject.com/) for the robust web framework
- [Bootstrap](https://getbootstrap.com/) for beautiful UI components
- [ReportLab](https://www.reportlab.com/) for PDF generation
- [Font Awesome](https://fontawesome.com/) for icons

## 📞 Support

- **GitHub Issues**: [Create an issue](https://github.com/rezashariatmadar/story-generator/issues)
- **Documentation**: See this README and inline code comments
- **Community**: Join discussions in GitHub Discussions

---

⭐ **Star this repository if you found it helpful!**

Built with ❤️ using Django and Google Gemini AI 