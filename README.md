# SmartLearn - AI-Powered Learning Platform

SmartLearn is an intelligent learning platform that uses AI to provide personalized learning experiences, course recommendations, and interactive assessments.

## Features

- 📊 Interactive Dashboard
- 📚 Course Management
- 📝 AI-Powered Assessments
- 📋 Task Planner
- 👥 Community Features
- ❓ Q&A System with AI Support

## Prerequisites

- Python 3.8 or higher
- MongoDB (local or Atlas)
- Git

## Setup Instructions

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd SmartLearn
   ```

2. **Create and activate a virtual environment**
   ```bash
   # Windows
   python -m venv venv 
   or 
   py -3.11 -m venv .venv

    .venv\\Scripts\\activate

   # Linux/Mac
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Create a `.env` file in the root directory with the following content:
   ```
   MONGO_URI=your_mongodb_connection_string
   ```
   Note: If you don't have a MongoDB connection string, the application will use a local fallback database for demo purposes.

5. **Run the application**
   ```bash
   streamlit run app.py
   ```

The application will be available at `http://localhost:8501`

## Project Structure

- `app.py` - Main application file
- `database.py` - Database connection and operations
- `ai_engine.py` - AI model integration and operations
- `granite_model.py` - IBM Granite model integration
- `pages/` - Contains different sections of the application
  - `dashboard.py` - Dashboard view
  - `courses.py` - Course management
  - `assessments.py` - Assessment system
  - `community.py` - Community features
  - `qa.py` - Q&A system
  - `todo.py` - Task planner

## Technical Details

### Database
- Uses MongoDB for data storage
- Includes fallback in-memory database for demo purposes
- Collections:
  - users
  - courses
  - assessments
  - community_posts
  - qa_questions
  - todos

### AI Integration
- Uses IBM Granite LLM for AI-powered features
- Provides personalized learning recommendations
- Generates assessment questions
- Answers user queries

### Frontend
- Built with Streamlit
- Responsive design
- Interactive components
- Real-time updates

## Troubleshooting

1. **Database Connection Issues**
   - Ensure MongoDB is running
   - Check your connection string in the `.env` file
   - The application will use a fallback database if connection fails

2. **Dependencies Issues**
   - Make sure you're using the correct Python version
   - Try updating pip: `python -m pip install --upgrade pip`
   - Reinstall requirements: `pip install -r requirements.txt --force-reinstall`

3. **Streamlit Issues**
   - Clear Streamlit cache: `streamlit cache clear`
   - Check if port 8501 is available

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 

Error handling:

cannot import name 'etree' from 'lxml':
 pip install --force-reinstall --upgrade lxml