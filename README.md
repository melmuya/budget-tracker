# 💰 Budget Tracker (Flask)

A simple, responsive budget-tracking web app built with Python and Flask. Users can set a budget, add and edit expenses, view spending summaries by category, filter expenses, and reset all data. It stores data locally in a JSON file — no database setup needed.

---

## 🚀 Features

- 💵 Set and reset an initial budget
- ✏️ Add and modify expenses
- 🔍 Filter expenses by category
- 📊 View totals by category
- ⚠️ Warnings when you're over budget or low on funds
- 📱 Fully responsive layout
- ❌ Erase all data and start fresh

---

## 🛠 Built With

- [Python 3](https://www.python.org/)
- [Flask](https://flask.palletsprojects.com/)
- HTML + CSS (vanilla)
- Local JSON storage (no external DB)

---

## 📸 Screenshots

![alt text](image-1.png)
![alt text](image.png)

---

## 🧪 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/melmuya/budget-tracker.git
cd budget-tracker

```
### 2. Create Virtual Environment

python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate


### 3. Install Dependencies

pip install flask


### 4. Run the App

python app.py


### Folder Structure

budget-tracker/
├── app.py
├── budget_tracker.py
├── budget_data.json       # Local data file (git-ignored)
├── static/
│   └── styles.css
├── templates/
│   ├── index.html
│   ├── edit.html
│   ├── categories.html
│   ├── filter.html
│   └── erase.html
└── README.md


### 📄 .gitignore

Make sure your .gitignore includes:
# Python
__pycache__/
*.pyc

# Virtual environment
venv/

# Local data file
budget_data.json


## 📄 License

This project is open for educational or personal use.
Feel free to fork it, build on it, and make it your own!


## 👤 Author

**Melchizedek Maranga**  
- [kingzedek.com](https://kingzedek.com)  
- [GitHub: @melmuya](https://github.com/melmuyayour-username)  
- [LinkedIn: https://www.linkedin.com/in/melchizedek-maranga/]  

```

