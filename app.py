from flask import Flask, render_template, request, redirect, url_for, flash
from budget_tracker import (get_total_expenses, get_balance)
from flask_sqlalchemy import SQLAlchemy
import os
from datetime import datetime
from dotenv import load_dotenv

from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash


load_dotenv() # Load environment variables from .env file
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY") 
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL") 
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

from flask_migrate import Migrate
migrate = Migrate(app, db)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # Specify the login route
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'


# Helper
def get_budget():
    if not current_user.is_authenticated:
        return 0
    budget = Budget.query.filter_by(user_id=current_user.id).first()
    return budget.amount if budget else 0

def set_budget(amount):
    if not current_user.is_authenticated:
        return 0

    budget = Budget.query.filter_by(user_id=current_user.id).first()
    
    if not budget:
        budget = Budget(amount=amount, user_id=current_user.id)
        db.session.add(budget)
        action = "created"
    else:
        old_amount = budget.amount
        budget.amount = amount
        action = f"updated from Ksh {old_amount}"
    db.session.commit()
    app.logger.info(f"Budget {action} to Ksh {amount}.")
    return amount


# Database Models
class Budget(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # nullable=True for migration

class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # nullable=True for migration

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(512), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationship to other models
    expenses = db.relationship('Expense', backref='user', lazy=True)
    budget = db.relationship('Budget', backref='user', lazy=True, uselist=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
        
    def __repr__(self):
        return f'<User {self.username}>'
    
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/register', methods=['GET', 'POST'])
def register():
    # Check if user is already logged in
    if current_user.is_authenticated:
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        username = request.form['username'].strip()
        email = request.form['email'].strip()
        password = request.form['password']
        password_confirm = request.form['password_confirm']
        
        # Simple validation
        if not username or not email or not password:
            flash('All fields are required', 'error')
            return redirect(url_for('register'))
            
        if password != password_confirm:
            flash('Passwords do not match', 'error')
            return redirect(url_for('register'))
            
        # Check if username or email already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'error')
            return redirect(url_for('register'))
            
        if User.query.filter_by(email=email).first():
            flash('Email already in use', 'error')
            return redirect(url_for('register'))
        
        # Create new user
        user = User(username=username, email=email)
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
        
    return render_template('register.html')
    
@app.route('/login', methods=['GET', 'POST'])
def login():
    # Check if user is already logged in
    if current_user.is_authenticated:
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        remember = 'remember' in request.form
        
        # Find the user
        user = User.query.filter_by(username=username).first()
        
        # Check if user exists and password is correct
        if not user or not user.check_password(password):
            flash('Invalid username or password', 'error')
            return redirect(url_for('login'))
            
        # Log the user in
        login_user(user, remember=remember)
        
        # Redirect to requested page or home
        next_page = request.args.get('next')
        if next_page:
            return redirect(next_page)
        return redirect(url_for('index'))
        
    return render_template('login.html')
    
@app.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out', 'info')
    return redirect(url_for('login'))



@app.route("/", methods=["GET", "POST"])
@login_required  # Ensure only logged-in users can access this route
def index():
    # budget, expenses = load_budget_data(DATA_FILE)
    budget = get_budget()
    expenses = Expense.query.filter_by(user_id=current_user.id).all()

    if budget == 0 and request.method == "POST" and "initial_budget" in request.form:
        # User is setting the initial budget
        try:
            initial_budget = float(request.form["initial_budget"].strip())
            set_budget(initial_budget)
        except ValueError:
            return "Invalid budget amount", 400
        return redirect("/")

    if request.method == "POST" and "description" in request.form:
        # User is adding an expense
        try:
            description = request.form["description"].strip().capitalize()
            amount = float(request.form["amount"].strip())
            category = request.form["category"].strip().capitalize()

            new_expense = Expense(description=description, amount=amount, category=category, user_id=current_user.id)
            db.session.add(new_expense)
            db.session.commit()

            flash("Added new expense: {description}", "success")

        except ValueError:
            flash("Invalid input. Please check your values.", "error")
            return redirect("/")

        return redirect("/")

    total_spent = get_total_expenses(expenses)
    balance = get_balance(budget, expenses)

    expense_dicts = [
        {
            "description": e.description,
            "amount": e.amount,
            "category": e.category.lower(),  # for consistency
            "created_at": e.created_at.strftime("%Y-%m-%d %H:%M")
        } for e in expenses
    ]

    return render_template(
        "index.html",
        budget=budget,
        expenses=expenses,
        total_spent=total_spent,
        balance=balance,
        expense_data=expense_dicts,
        user=current_user
    )

@app.route("/edit-budget", methods=["GET", "POST"])
@login_required  # Ensure only logged-in users can access this route
def edit_budget():
    budget = get_budget()
    
    if request.method == "POST":
        try:
            new_budget = float(request.form["new_budget"].strip())
            
            # Basic validation
            if new_budget <= 0:
                flash("Budget must be greater than zero.", "error")
                return redirect(url_for("edit_budget"))
                
            # Update the budget
            set_budget(new_budget)
            
            flash(f"Budget successfully updated to Ksh {new_budget}.", "success")
            return redirect(url_for("index"))
            
        except ValueError:
            flash("Invalid budget amount. Please enter a valid number.", "error")
            return redirect(url_for("edit_budget"))
    
    # GET request - display the edit form
    return render_template("edit_budget.html", budget=budget)

@app.route("/edit/<int:expense_id>", methods=["GET", "POST"])
@login_required  # Ensure only logged-in users can access this route
def edit_expense(expense_id):
    
    # expense = db.session.get(Expense, expense_id) # Get by ID, not list index
    expense = Expense.query.filter_by(id=expense_id, user_id=current_user.id).first() # Ensure it's the user's expense

    if not expense:
        return "Expense not found", 404

    if request.method == "POST":
        try:
            expense.description = request.form["description"].strip().capitalize()
            expense.amount = float(request.form["amount"].strip())
            expense.category = request.form["category"].strip().capitalize()
            db.session.commit()

            flash("Expense updated successfully", "success") 
        except ValueError:
            flash("Invalid input.", "error")
            return redirect("/")
        return redirect(url_for("index"))

    return render_template("edit.html", index=index, expense=expense)


@app.route("/categories")
@login_required  # Ensure only logged-in users can access this route
def show_by_category():
    expenses = Expense.query.filter_by(user_id=current_user.id).all()

    category_totals = {}
    for expense in expenses:
        category = expense.category
        category_totals[category] = category_totals.get(category, 0) + expense.amount

    return render_template("categories.html", category_totals=category_totals)


@app.route("/filter", methods=["GET", "POST"])
@login_required  # Ensure only logged-in users can access this route
def filter_by_category():
    filtered_expenses = []
    selected_category = ""

    if request.method == "POST":
        selected_category = request.form["category"].strip().capitalize()
        filtered_expenses = Expense.query.filter_by(category=selected_category, user_id=current_user.id).all()

    return render_template(
        "filter.html",
        filtered_expenses=filtered_expenses,
        selected_category=selected_category
    )


@app.route("/erase", methods=["GET", "POST"])
@login_required  # Ensure only logged-in users can access this route
def erase_data():
    if request.method == "POST":
        # Only delete the current user's data
        Budget.query.filter_by(user_id=current_user.id).delete()
        Expense.query.filter_by(user_id=current_user.id).delete()
        db.session.commit()
        flash("All data erased. Starting anew.", "info")
        return redirect("/")

    return render_template("erase.html")


# Temporary test model
class TestEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.String(100), nullable=False)

# Route to test DB
@app.route("/test-db")
def test_db():
    try:
        db.create_all()  # Ensure table exists

        # Add new test entry
        entry = TestEntry(message="Hello from the database!")
        db.session.add(entry)
        db.session.commit()

        # Fetch all entries
        entries = TestEntry.query.all()
        return "<br>".join([f"{e.id}: {e.message}" for e in entries])

    except Exception as e:
        return f"Error: {str(e)}"


# with app.app_context():
#     db.create_all()


if __name__ == "__main__":
    app.run(debug=True)
