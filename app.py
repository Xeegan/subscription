import sqlite3
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns

# Fungsi untuk membuat koneksi ke database SQLite
def create_connection():
    conn = sqlite3.connect('subscriptions.db')
    return conn

# Fungsi untuk membuat tabel subscriptions jika belum ada
def create_table():
    conn = create_connection()
    cursor = conn.cursor()
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
    conn.commit()
    conn.close()

# Fungsi untuk menyisipkan data ke dalam tabel subscriptions
def insert_subscription(customer_name, customer_email, subscription_type, status, start_date, end_date):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO subscriptions (customer_name, customer_email, subscription_type, status, start_date, end_date)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (customer_name, customer_email, subscription_type, status, start_date, end_date))
    conn.commit()
    conn.close()

# Fungsi untuk mengambil data subscription dari database
def get_subscription_data():
    conn = create_connection()
    query = '''
    SELECT status, COUNT(*) as count
    FROM subscriptions
    GROUP BY status
    '''
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

# Fungsi utama untuk menjalankan aplikasi Streamlit
def run_streamlit_app():
    st.title("Subscription Status Dashboard")

    # Tampilkan data subscription
    st.write("## Subscription Data")
    data = get_subscription_data()
    st.dataframe(data)

    # Visualisasi data menggunakan grafik batang
    st.write("## Subscription Status Visualization")
    fig, ax = plt.subplots()
    sns.barplot(data=data, x='status', y='count', ax=ax)
    st.pyplot(fig)

    # Form untuk menambahkan subscription baru
    st.write("## Add New Subscription")
    with st.form(key='subscription_form'):
        customer_name = st.text_input('Customer Name')
        customer_email = st.text_input('Customer Email')
        subscription_type = st.selectbox('Subscription Type', ['Basic', 'Standard', 'Premium'])
        status = st.selectbox('Status', ['Ongoing', 'Cancelled', 'Unpaid'])
        start_date = st.date_input('Start Date')
        end_date = st.date_input('End Date', help="Leave empty for ongoing subscriptions")
        submit_button = st.form_submit_button(label='Add Subscription')

        if submit_button:
            insert_subscription(customer_name, customer_email, subscription_type, status, str(start_date), str(end_date))
            st.success("Subscription added successfully!")

if __name__ == "__main__":
    create_table()  # Pastikan tabel sudah ada
    run_streamlit_app()
