# Streamlit Basic App

A simple and interactive web application built with [Streamlit](https://streamlit.io/) and Python.

## 🚀 Features

- ✅ Real-time, responsive user interface
- ✅ Text input for user name
- ✅ Age selection using a slider
- ✅ Personalized greeting based on user input

## 📋 Requirements

- Python 3.7 or higher
- Streamlit

## 📦 Installation

Follow the steps below to set up and run the application:

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/streamlit-basic-app.git
cd streamlit-basic-app
```

### 2. Create and Activate Virtual Environment

- On macOS/Linux:
```bash
python -m venv env
source env/bin/activate
```

- On Windows:
```bash
python -m venv env
env\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the App

```bash
streamlit run app/main.py
```

# 📁 Project Structure

```text
.
├── README.md
├── requirements.txt
├── app/
│   ├── main.py
│   └── utils
└── env
```

- `app/main.py`: Main Streamlit app entry point.
- `app/utils/`: Utility modules for document, image, and OCR processing.
- `.streamlit/config.toml`: Streamlit configuration file.
- `requirements.txt`: List of project dependencies.
- `env/`: Python virtual environment (should not be committed to version control).
- `README.md`: Project documentation.

> **Note:** The `env/` folder is your local virtual environment and should be excluded from version control (add to `.gitignore`).
