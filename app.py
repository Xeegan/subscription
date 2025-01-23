import streamlit as st
import pandas as pd
import datetime
import hashlib
import random

# Fungsi untuk membaca dataset langganan
def load_data():
    try:
        df = pd.read_csv("subscriptions.csv")
        return df
    except FileNotFoundError:
        # Jika file tidak ada, buat dataset kosong
        return pd.DataFrame(columns=["id", "user_name", "plan_type", "start_date", "end_date", "is_active", "role"])

# Fungsi untuk membaca dataset pengguna
def load_users():
    try:
        users = pd.read_csv("users.csv")
        return users
    except FileNotFoundError:
        return pd.DataFrame(columns=["user_name", "password", "role", "email", "otp"])

# Fungsi untuk menyimpan data ke dalam dataset
def save_data(df):
    df.to_csv("subscriptions.csv", index=False)

def save_users(users):
    users.to_csv("users.csv", index=False)

# Fungsi untuk mencatat transaksi
def log_transaction(user_name, action, details):
    try:
        # Menangani file kosong atau tidak ada
        try:
            transactions = pd.read_csv("transactions.csv")
        except FileNotFoundError:
            transactions = pd.DataFrame(columns=["id", "user_name", "action", "timestamp", "details"])

        new_transaction = pd.DataFrame({
            "id": [len(transactions) + 1],
            "user_name": [user_name],
            "action": [action],
            "timestamp": [datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
            "details": [details]
        })
        transactions = pd.concat([transactions, new_transaction], ignore_index=True)
        transactions.to_csv("transactions.csv", index=False)
    except Exception as e:
        st.error(f"Error logging transaction: {str(e)}")

# Fungsi untuk hashing password
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Fungsi untuk mengirim OTP
def send_otp(email):
    otp = random.randint(100000, 999999)
    # Simulasi pengiriman OTP (contoh: bisa menggunakan API email)
    st.info(f"Simulated OTP sent to {email}: {otp}")
    return otp

# Fungsi untuk registrasi
def register_user(users, user_name, password, role, email):
    if user_name in users["user_name"].values:
        return False, "User already exists."

    hashed_password = hash_password(password)
    otp = send_otp(email)
    new_user = pd.DataFrame({
        "user_name": [user_name],
        "password": [hashed_password],
        "role": [role],
        "email": [email],
        "otp": [otp]
    })
    users = pd.concat([users, new_user], ignore_index=True)
    save_users(users)
    return True, "Registration successful. Please verify your email with the OTP sent."

# Fungsi untuk verifikasi OTP
def verify_otp(users, user_name, entered_otp):
    user = users[users["user_name"] == user_name]
    if not user.empty and int(user.iloc[0]["otp"]) == int(entered_otp):
        users.loc[users["user_name"] == user_name, "otp"] = None  # Clear OTP after verification
        save_users(users)
        return True, "OTP verification successful."
    return False, "Invalid OTP."

# Fungsi untuk login
def login_user(users, user_name, password):
    hashed_password = hash_password(password)
    user = users[(users["user_name"] == user_name) & (users["password"] == hashed_password)]
    if not user.empty and pd.isna(user.iloc[0]["otp"]):
        return True, user.iloc[0]["role"]
    elif not pd.isna(user.iloc[0]["otp"]):
        return False, "Please verify your account using the OTP sent to your email."
    return False, "Invalid username or password."

# Fungsi untuk memeriksa status langganan
def check_status(row):
    today = datetime.datetime.now()
    end_date = datetime.datetime.strptime(row["end_date"], "%Y-%m-%d")
    if today > end_date:
        return False
    return True

# Fungsi untuk menganalisis data langganan
def analyze_data(df):
    st.subheader("Data Analysis")
    if df.empty:
        st.warning("No subscription data available.")
        return

    # Menampilkan statistik dasar
    st.write("Summary Statistics:")
    st.write(df.describe(include="all"))

    # Total langganan aktif
    active_subscriptions = df[df["is_active"]].shape[0]
    st.write(f"Total Active Subscriptions: {active_subscriptions}")

    # Distribusi tipe langganan
    st.write("Subscription Plan Distribution:")
    plan_counts = df["plan_type"].value_counts()
    st.bar_chart(plan_counts)

    # Langganan yang segera kedaluwarsa
    today = datetime.datetime.now()
    df["days_until_expiry"] = pd.to_datetime(df["end_date"]) - today
    expiring_soon = df[df["days_until_expiry"] <= pd.Timedelta(days=7)]
    if not expiring_soon.empty:
        st.write("Subscriptions Expiring Soon:")
        st.write(expiring_soon[["user_name", "plan_type", "end_date"]])
    else:
        st.write("No subscriptions expiring within the next 7 days.")

def main():
    st.title("Advanced Subscription Management System")

    # Load data dari file CSV
    df = load_data()
    users = load_users()

    # Inisialisasi session state untuk login
    if "is_logged_in" not in st.session_state:
        st.session_state.is_logged_in = False
        st.session_state.user_name = None
        st.session_state.role = None

    if not st.session_state.is_logged_in:
        # Autentikasi
        st.subheader("Authentication")
        auth_mode = st.radio("Choose mode:", ["Login", "Register"])

        user_name = st.text_input("User Name:")
        password = st.text_input("Password:", type="password")

        if auth_mode == "Register":
            role = st.radio("Role:", ["User", "Admin"])
            email = st.text_input("Email:")
            if st.button("Register"):
                success, message = register_user(users, user_name, password, role, email)
                if success:
                    st.success(message)
                else:
                    st.error(message)

        elif auth_mode == "Login":
            if st.button("Login"):
                success, role_or_message = login_user(users, user_name, password)
                if success:
                    st.session_state.is_logged_in = True
                    st.session_state.user_name = user_name
                    st.session_state.role = role_or_message
                    st.success(f"Welcome, {user_name}! Role: {role_or_message}")
                else:
                    st.error(role_or_message)

            otp_verification = st.text_input("Enter OTP (if required):")
            if st.button("Verify OTP"):
                verified, message = verify_otp(users, user_name, otp_verification)
                if verified:
                    st.success(message)
                else:
                    st.error(message)

    else:
        st.success(f"Logged in as {st.session_state.user_name} ({st.session_state.role})")

        # Menambahkan fitur Logout
        if st.button("Logout"):
            st.session_state.is_logged_in = False
            st.session_state.user_name = None
            st.session_state.role = None
            st.success("You have been logged out.")

        if st.session_state.role == "User":
            user_name = st.session_state.user_name
            user_data = df[df["user_name"] == user_name]

            if not user_data.empty:
                user_row = user_data.iloc[0]
                st.write(f"Subscription for {user_name} is {'active' if user_row['is_active'] else 'inactive'} until {user_row['end_date']}.")

                if not check_status(user_row):
                    st.error(f"Your subscription has expired on {user_row['end_date']}. Please renew or change your plan.")

                new_plan = st.radio("Change your plan to:", ("monthly", "yearly"))

                if st.button(f"Change to {new_plan} plan"):
                    if update_subscription(df, user_name, new_plan):
                        st.success(f"Subscription plan for {user_name} updated to {new_plan}.")
                    else:
                        st.error(f"Failed to update the subscription for {user_name}.")

                if st.button("Cancel Subscription"):
                    if cancel_subscription(df, user_name):
                        st.success(f"Subscription for {user_name} has been cancelled.")
                    else:
                        st.error(f"Failed to cancel the subscription for {user_name}.")

            else:
                st.warning(f"No active subscription found for {user_name}.")

                plan_type = st.radio("Choose your plan type:", ("monthly", "yearly"))
                if st.button("Create Subscription"):
                    new_id = len(df) + 1
                    new_start_date = datetime.datetime.now().strftime("%Y-%m-%d")
                    new_end_date = (datetime.datetime.now() + datetime.timedelta(days=30) if plan_type == "monthly" else datetime.datetime.now() + datetime.timedelta(days=365)).strftime("%Y-%m-%d")
                    new_subscription = pd.DataFrame({
                        "id": [new_id],
                        "user_name
