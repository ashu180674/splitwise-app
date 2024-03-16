from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import sqlite3

app = FastAPI()

# Allow requests from localhost:3000
origins = [
"*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Initialize SQLite database
conn = sqlite3.connect('split_ease.db')
c = conn.cursor()

# Create expenses table if not exists
c.execute('''CREATE TABLE IF NOT EXISTS expenses
             (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id TEXT, description TEXT, amount REAL)''')
conn.commit()


@app.post('/add_expense')
async def add_expense(data: dict):
    user_id = data['user_id']
    description = data['description']
    amount = data['amount']
    shared_with = data.get('shared_with', [])

    conn = sqlite3.connect('split_ease.db')
    c = conn.cursor()

    # Distribute the expense equally among all users
    total_users = len(shared_with) + 1  # Add 1 for the user submitting the expense
    split_amount = int(amount) / int(total_users)

    # Insert expense for the user who submitted it
    c.execute("INSERT INTO expenses (user_id, description, amount) VALUES (?, ?, ?)",
              (user_id, description, split_amount))

    # Insert expense for each user shared with
    for shared_user in shared_with:
        c.execute("INSERT INTO expenses (user_id, description, amount) VALUES (?, ?, ?)",
                  (shared_user, description, split_amount))

    conn.commit()
    conn.close()

    return {'message': 'Expense added successfully'}


@app.get('/get_balance/{user_id}')
async def get_balance(user_id: str):
    conn = sqlite3.connect('split_ease.db')
    c = conn.cursor()

    c.execute("SELECT SUM(amount) FROM expenses WHERE user_id = ?", (user_id,))
    result = c.fetchone()
    balance = result[0] if result else 0

    conn.close()

    return {'balance': balance}
