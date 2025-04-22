from flask import Flask, render_template, request, redirect
from budget_tracker import (add_expense, get_total_expenses, get_balance, show_budget_details, load_budget_data, save_budget_details, show_expenses_by_category, filter_expenses_by_category)
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# Database Models
class Budget(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)

class Expense():
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    

DATA_FILE = "budget_data.json"

@app.route("/", methods=["GET", "POST"])
def index():
    budget, expenses = load_budget_data(DATA_FILE)

    if budget == 0 and request.method == "POST" and "initial_budget" in request.form:
        # User is setting the initial budget
        budget = float(request.form["initial_budget"])
        save_budget_details(DATA_FILE, budget, expenses)
        return redirect("/")

    if request.method == "POST" and "description" in request.form:
        # User is adding an expense
        description = request.form["description"].capitalize()
        amount = float(request.form["amount"])
        category = request.form["category"].capitalize()
        add_expense(expenses, description, amount, category)
        save_budget_details(DATA_FILE, budget, expenses)
        return redirect("/")

    total_spent = get_total_expenses(expenses)
    balance = get_balance(budget, expenses)

    return render_template(
        "index.html",
        budget=budget,
        expenses=expenses,
        total_spent=total_spent,
        balance=balance
    )

@app.route("/edit/<int:index>", methods=["GET", "POST"])
def edit_expense(index):
    budget, expenses = load_budget_data(DATA_FILE)

    if index < 0 or index >= len(expenses):
        return "Expense not found", 404

    if request.method == "POST":
        new_description = request.form["description"]
        new_amount = float(request.form["amount"])
        new_category = request.form["category"]

        expenses[index]["Description"] = new_description
        expenses[index]["Amount"] = new_amount
        expenses[index]["Category"] = new_category

        save_budget_details(DATA_FILE, budget, expenses)
        return redirect("/")

    expense = expenses[index]
    return render_template("edit.html", index=index, expense=expense)


@app.route("/categories")
def show_by_category():
    budget, expenses = load_budget_data(DATA_FILE)

    category_totals = {}
    for expense in expenses:
        category = expense["Category"]
        category_totals[category] = category_totals.get(category, 0) + expense["Amount"]

    return render_template("categories.html", category_totals=category_totals)


@app.route("/filter", methods=["GET", "POST"])
def filter_by_category():
    budget, expenses = load_budget_data(DATA_FILE)

    filtered_expenses = []
    selected_category = ""

    if request.method == "POST":
        selected_category = request.form["category"].capitalize()
        filtered_expenses = [
            expense for expense in expenses
            if expense["Category"] == selected_category
        ]

    return render_template(
        "filter.html",
        filtered_expenses=filtered_expenses,
        selected_category=selected_category
    )


@app.route("/erase", methods=["GET", "POST"])
def erase_data():
    budget, expenses = load_budget_data(DATA_FILE)

    if request.method == "POST":
        save_budget_details(DATA_FILE, 0, [])
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


with app.app_context():
    db.create_all()


if __name__ == "__main__":
    app.run(debug=True)
