from flask import Flask, request, Response
from twilio.twiml.messaging_response import MessagingResponse
import mysql.connector
import re

app = Flask(__name__)

# MySQL DB connection
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="yaswanth21",
        database="expense_bot"
    )

# Add expense to DB
def add_expense(category, amount):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO expenses (category, amount) VALUES (%s, %s)", (category, amount))
    conn.commit()
    cursor.close()
    conn.close()

# Get total for a category
def get_total(category):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT SUM(amount) FROM expenses WHERE category = %s", (category,))
    result = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return result if result else 0

@app.route("/bot", methods=["POST"])
def bot():
    incoming_msg = request.values.get("Body", "").lower().strip()
    print(f"Received message: {incoming_msg}")  # Add this for debugging

    resp = MessagingResponse()
    msg = resp.message()

    match = re.match(r"^(\w+)\s+(\d+)$", incoming_msg)
    if match:
        category = match.group(1)
        amount = int(match.group(2))
        add_expense(category, amount)
        print(f"✅ Added {amount} to {category}.")
        msg.body(f"✅ Added {amount} to {category}.")
    elif incoming_msg.startswith("total"):
        parts = incoming_msg.split()
        if len(parts) == 2:
            category = parts[1]
            total = get_total(category)
            print(f"📊 Total spent on {category}: {total}")
            msg.body(f"📊 Total spent on {category}: {total}")
        else:
            msg.body("❗ Use format: total <category>")
    else:
        msg.body("👋 Send like 'groceries 100' or 'total groceries'.")

    # ✅ Correct way to return response for Twilio
    return Response(str(resp), mimetype="application/xml")

if __name__ == "__main__":
    app.run(port=5000, debug=True)

    
# @app.route("/bot", methods=["POST"])
# def bot():
#     incoming_msg = request.values.get('Body', '').lower()
#     print(f"Received message: {incoming_msg}")
#     resp = MessagingResponse()
#     msg = resp.message()

#     if 'tea' in incoming_msg:
#         msg.body("You ordered tea ☕️")
#     else:
#         msg.body("Sorry, I didn't understand that.")

#     return str(resp)

"""if __name__ == "__main__":
    app.run(port=5000, debug=True)"""
