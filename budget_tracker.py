import json
from datetime import datetime

def add_expense(expenses, description, amount, category):
    expenses.append(
        {
            "Description": description, 
            "Amount": amount, 
            "Category": category,
            "Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    )
    print(f"Added expense: {description}, Amount: {amount}")


def get_total_expenses(expenses):
    # total = 0
    # for expense in expenses:
    #     total += expense["Amount"]
    # return total
    return sum(expense.amount for expense in expenses)

def get_balance(budget, expenses):
    balance = budget - get_total_expenses(expenses)
    return balance


def show_budget_details(budget, expenses):
    print(f"\nTotal budget: {budget}")
    print("Expenses:")
    for expense in expenses:
        print(f" - {expense['Description']} ({expense['Category']}): {expense['Amount']}")
    print(f"Total spent: {get_total_expenses(expenses)}")
    print(f"Remaining budget: {get_balance(budget, expenses)}\n")


def load_budget_data(filepath):
    try:
        with open(filepath, "r") as file:
            data = json.load(file)    
            return data["initial_budget"], data["expenses"]        
    except (FileNotFoundError, json.JSONDecodeError):
        return 0, [] # return default values if the file doesn't exist or is empty/corrupted
        

def save_budget_details(filepath, initial_budget, expenses):
    data = {
        "initial_budget": initial_budget,
        "expenses": expenses
    }
    with open(filepath, "w") as file:
        json.dump(data, file, indent=4)


def show_expenses_by_category(expenses):  # New function
    categories = {}
    for expense in expenses:
        category = expense["Category"]
        if category not in categories:
            categories[category] = 0
        categories[category] += expense["Amount"]
    for category in sorted(categories.keys()):
        print(f"{category}: {categories[category]}")



def filter_expenses_by_category(expenses):
    category = input("Enter the category to filter by: ").capitalize()
    filtered_expenses = [expense for expense in expenses if expense["Category"] == category]

    if filtered_expenses:
        print(f"\nExpenses in category '{category}':")
        for expense in filtered_expenses:
            print(f" - {expense['Description']}: {expense['Amount']} (Date: {expense['Date']})")
    else:
        print(f"No expenses found in category '{category}'.")


def main():
    print("Welcome to the Budget app.")
    filepath = "budget_data.json"  # Define the path to your json file
    initial_budget, expenses = load_budget_data(filepath)
    if initial_budget == 0:
        initial_budget = float(input("Please enter your initial budget: "))
    budget = initial_budget

    while True:
        print("\nWhat would you like to do?")
        print("1. Add an expense") #POST
        print("2. Show budget details")
        print("3. Modify an expense") #POST
        print("4. Show expenses by category")  # New option
        print("5. Filter expenses by category")  # New option
        print("6. Erase all data (start anew)")
        print("7. Save and Exit")
        user_choice = input("Enter your choice (1/2/3/4/5/6/7): ")

        if user_choice == "1":
            description = input("Enter expense description: ").strip().capitalize()
            amount = float(input("Enter amount: "))
            category = input("Enter category (e.g. Food, Transport, etc.): ").strip().capitalize()
            add_expense(expenses, description, amount, category)
        elif user_choice == "2":
            show_budget_details(budget, expenses)
        elif user_choice == "3":
            print("Current expenses:")
            for i, expense in enumerate(expenses):
                print(f"{i + 1}. {expense['Description']}: {expense['Amount']}")
            try:
                index = int(input("Enter the number of the expense to modify: ")) - 1
                if 0 <= index < len(expenses):
                    new_description = input("Enter new description (leave blank to keep current): ")
                    new_amount = input("Enter new amount (leave blank to keep current): ")
                    new_category = input("Enter new category (leave blank to keep current): ")
                    if new_description:
                        expenses[index]["Description"] = new_description
                    if new_amount:
                        expenses[index]["Amount"] = float(new_amount)
                    if new_category:
                        expenses[index]["Category"] = new_category
                    print("Expense updated successfully.")
                else:
                    print("Invalid expense number.")
            except ValueError:
                print("Invalid input. Please enter a valid number.")
        elif user_choice == "4":  # New feature
            show_expenses_by_category(expenses)
        elif user_choice == "5":  # New feature
            filter_expenses_by_category(expenses)
        elif user_choice == "6":
            confirm = input("Are you sure you want to erase all data? (yes/no): ").lower()
            if confirm == "yes":
                initial_budget = 0
                budget = 0
                expenses.clear()
                save_budget_details(filepath, initial_budget, expenses)
                print("All data erased. Starting anew.")
            else:
                print("Erase operation canceled.")
        elif user_choice == "7":
            save_budget_details(filepath, initial_budget, expenses)
            print("Exiting Budget App. Goodbye!")
            break
        else:
            print("Invalid option. Please choose again.")

if __name__ == "__main__":
    main()