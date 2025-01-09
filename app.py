import sqlite3

# Connect to the database (or create it if it doesn't exist)
conn = sqlite3.connect('subscriptions.db')

# Create a cursor object
cursor = conn.cursor()

# Create the 'subscriptions' table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS subscriptions (
        subscription_id INTEGER PRIMARY KEY,
        customer_name TEXT NOT NULL,
        customer_email TEXT NOT NULL,
        subscription_type TEXT NOT NULL,
        status TEXT NOT NULL,
        start_date TEXT NOT NULL,
        end_date TEXT
    )
''')

# Commit the changes and close the connection
conn.commit()
conn.close()

print("Database and 'subscriptions' table created successfully!")

import sqlite3

# Function to insert a new subscription
def insert_subscription(customer_name, customer_email, subscription_type, status, start_date, end_date):
    conn = sqlite3.connect('subscriptions.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO subscriptions (customer_name, customer_email, subscription_type, status, start_date, end_date)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (customer_name, customer_email, subscription_type, status, start_date, end_date))
    conn.commit()
    conn.close()

# Example usage
insert_subscription('Rangga', 'rangga@gmail.com', 'Premium', 'cancelled', '2025-01-01', '2025-12-31')
insert_subscription('Yavin', 'yavin@gmail.com', 'Basic', 'Unpaid', '2025-01-01', None)
insert_subscription('Nicky', 'nicky@gmail.com', 'Standard', 'cancelled', '2025-01-01', '2025-06-30')
insert_subscription('Rafif', 'rafif@gmail.com', 'Premium', 'Ongoing', '2025-01-01', '2025-12-31')

print("Sample subscriptions inserted successfully!")

import sqlite3

# Function to retrieve all subscriptions
def retrieve_subscriptions():
    conn = sqlite3.connect('subscriptions.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM subscriptions')
    subscriptions = cursor.fetchall()
    conn.close()
    return subscriptions

# Example usage
subscriptions = retrieve_subscriptions()
for subscription in subscriptions:
    print(subscription)

!pip install streamlit pyngrok

%%writefile app.py
import sqlite3
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns

# Function to retrieve data from the database
def get_subscription_data():
    conn = sqlite3.connect('subscriptions.db')
    query = '''
    SELECT status, COUNT(*) as count
    FROM subscriptions
    GROUP BY status
    '''
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

# Streamlit app
st.title("Subscription Status Dashboard")

# Retrieve data
data = get_subscription_data()

# Display data as a table
st.write("## Subscription Data")
st.dataframe(data)

# Visualize data
st.write("## Subscription Status Visualization")
fig, ax = plt.subplots()
sns.barplot(data=data, x='status', y='count', ax=ax)
st.pyplot(fig)

! wget -q -O - ipv4.icanhazip.com

! streamlit run app.py & npx localtunnel --port 8501
