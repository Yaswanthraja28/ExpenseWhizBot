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
        password="",
        database=""
    )

# Add expense to DB
def add_expense(user_number, category, amount):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO expenses (user_number ,category, amount) VALUES (%s, %s, %s)",
        (user_number, category, amount))
    conn.commit()
    cursor.close()
    conn.close()

# Get total for a category
def get_total(user_number,category):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT SUM(amount) FROM expenses WHERE user_number = %s AND category = %s",
        (user_number, category)
    )
    result = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return result if result else 0

@app.route("/bot", methods=["POST"])
def bot():
    incoming_msg = request.values.get("Body", "").lower().strip()
    user_number = request.values.get("From", "")  # Get sender's WhatsApp number
    print(f"📩 Received message from {user_number}: {incoming_msg}")

    resp = MessagingResponse()
    msg = resp.message()

    match = re.match(r"^(\w+)\s+(\d+)$", incoming_msg)
    if match:
        category = match.group(1)
        amount = int(match.group(2))
        add_expense(user_number, category, amount)
        print(f"✅ Added {amount} to {category}.")
        msg.body(f"✅ Added {amount} to {category}.")
    elif incoming_msg.startswith("total"):
        parts = incoming_msg.split()
        if len(parts) == 2:
            category = parts[1]
            total = get_total(user_number ,category)
            print(f"📊 Total spent on {category} for {user_number}: {total}")
            msg.body(f"📊 Total spent on {category}: {total}")
        else:
            msg.body("❗ Use format: total <category>")
    else:
        msg.body("👋 Send like 'groceries 100' or 'total groceries'.")

    # ✅ Correct way to return response for Twilio
    return Response(str(resp), mimetype="application/xml")

if __name__ == "__main__":
    app.run(port=5000, debug=True)


"""if __name__ == "__main__":
    app.run(port=5000, debug=True)"""
