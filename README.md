# Content Pipeline AI

Content Pipeline AI is an AI-powered content generation application that transforms topics and article URLs into ready-to-use content for different platforms.

## Features

- Generate structured blog posts.
- Create exactly five posts for X (Twitter).
- Generate professional LinkedIn posts.
- Extract content from article URLs.
- Copy generated content with one click.
- Input validation and error handling.
- Application logging.
- Automated testing with pytest.

## Technologies Used

- Python
- Flask
- Anthropic Claude API
- HTML, CSS and JavaScript
- BeautifulSoup
- Requests
- Pytest
- Gunicorn

## Installation

Clone the repository and navigate into the project directory.

Create and activate a virtual environment:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

Install the required dependencies:

```powershell
pip install -r requirements.txt
```

## Environment Configuration

Create a `.env` file in the project root and configure your Anthropic API credentials.

The application uses environment variables to securely access the Anthropic API.

Never upload your actual `.env` file to GitHub.

## Running the Application

Start the application:

```powershell
python app.py
```

Open your browser and visit:

`http://127.0.0.1:5000`

## Running Tests

Run the automated test suite:

```powershell
pytest -v
```

## Project Structure

```text
my-advanced-app/
├── app.py
├── pipeline.py
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
├── logs/
└── tests/
    ├── conftest.py
    └── test_pipeline.py
```

## Future Improvements

- User authentication.
- Monthly subscription plans.
- Usage limits.
- Payment integration.
- Cloud deployment.

## Author

Developed as part of the AI Masterclass practical projects.