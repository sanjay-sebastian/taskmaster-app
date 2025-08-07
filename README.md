# TaskMaster App

TaskMaster is a full-stack task management application powered by Flask. It offers a RESTful API backend that manages user accounts and task tracking functionality. The app also supports serving a static frontend, making it easy to deploy as a standalone project or part of a microservice architecture.

---

## 🚀 Features

- User authentication & management (via `user_bp`)
- Task creation, tracking, and management (via `task_bp`)
- RESTful API design
- Cross-Origin Resource Sharing (CORS) support
- Supports both local SQLite or external database (via `DATABASE_URL`)
- Serves frontend from `static/` folder
- Modular architecture for scalability

---

## 🛠️ Tech Stack

- **Backend**: Python, Flask, Flask-CORS, Flask-SQLAlchemy
- **Database**: SQLite (default), PostgreSQL/MySQL (optional via `DATABASE_URL`)
- **Structure**:
  - `src/models/`: SQLAlchemy models (e.g. User, Task)
  - `src/routes/`: Blueprint routes for API
  - `static/`: Frontend build (e.g. React/Vue/HTML)
  - `database/`: Local SQLite DB (if no external DB provided)

---

## 📦 Installation

### 🔧 Prerequisites
- Python 3.7+
- pip
- (Optional) virtualenv

### 📥 Steps

```bash
# Clone the repository
git clone https://github.com/sanjay-sebastian/taskmaster-app.git
cd taskmaster-app

# (Optional) Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
