from flask import Flask, render_template, request, redirect, url_for, flash
from budget_tracker import (get_total_expenses, get_balance)
from flask_sqlalchemy import SQLAlchemy
import os
from datetime import datetime
from dotenv import load_dotenv


load_dotenv() # Load environment variables from .env file
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY") 
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL") 
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

from flask_migrate import Migrate
migrate = Migrate(app, db)


# Helper
def get_budget():
    budget = Budget.query.first()
    return budget.amount if budget else 0

def set_budget(amount):
    budget = Budget.query.first()
    if not budget:
        budget = Budget(amount=amount)
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

class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    

@app.route("/", methods=["GET", "POST"])
def index():
    # budget, expenses = load_budget_data(DATA_FILE)
    budget = get_budget()
    expenses = Expense.query.all()

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

            new_expense = Expense(description=description, amount=amount, category=category)
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
    )

@app.route("/edit-budget", methods=["GET", "POST"])
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
def edit_expense(expense_id):
    
    expense = db.session.get(Expense, expense_id) # Get by ID, not list index

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
def show_by_category():
    budget = get_budget()
    expenses = Expense.query.all()

    category_totals = {}
    for expense in expenses:
        category = expense.category
        category_totals[category] = category_totals.get(category, 0) + expense.amount

    return render_template("categories.html", category_totals=category_totals)


@app.route("/filter", methods=["GET", "POST"])
def filter_by_category():
    budget = get_budget()
    expenses = Expense.query.all()

    filtered_expenses = []
    selected_category = ""

    if request.method == "POST":
        selected_category = request.form["category"].strip().capitalize()
        filtered_expenses = Expense.query.filter_by(category=selected_category).all()

    return render_template(
        "filter.html",
        filtered_expenses=filtered_expenses,
        selected_category=selected_category
    )


@app.route("/erase", methods=["GET", "POST"])
def erase_data():
    if request.method == "POST":
        set_budget(0)
        Expense.query.delete()
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
