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
    st.info(f"Simulated OTP sent to {email}: {otp}")
    return otp

# Fungsi untuk registrasi
def register_user(users, user_name, password, role, email):
    if user_name in users["user_name"].values:
        return False, "User  already exists."

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
        users.loc[users["user_name"] == user_name, "otp"] = None
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

# Fungsi untuk memperbarui langganan
def update_subscription(df, user_name, new_plan):
    today = datetime.datetime.now()
    end_date = today + datetime.timedelta(days=30 if new_plan == "monthly" else 365)

    if user_name in df["user_name"].values:
        df.loc[df["user_name"] == user_name, ["plan_type", "start_date", "end_date", "is_active"]] = [
            new_plan, today.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"), True
        ]
    else:
        new_subscription = pd.DataFrame({
            "id": [len(df) + 1],
            "user_name": [user_name],
            "plan_type": [new_plan],
            "start_date": [today.strftime("%Y-%m-%d")],
            "end_date": [end_date.strftime("%Y-%m-%d")],
            "is_active": [True],
            "role": ["User "]
        })
        df = pd.concat([df, new_subscription], ignore_index=True)

    save_data(df)
    log_transaction(user_name, "Update Subscription", f"Changed plan to {new_plan}")
    return True

# Fungsi untuk membatalkan langganan
def cancel_subscription(df, user_name):
    if user_name in df["user_name"].values:
        df.loc[df["user_name"] == user_name, "is_active"] = False
        save_data(df)
        log_transaction(user_name, "Cancel Subscription", "Subscription cancelled.")
        return True
    return False

# Fungsi untuk menganalisis data langganan
def analyze_data(df):
    st.subheader("Data Analysis")
    if df.empty:
        st.warning("No subscription data available.")
        return

    st.write("Summary Statistics:")
    st.write(df.describe(include="all"))

    active_subscriptions = df[df["is_active"]].shape[0]
    st.write(f"Total Active Subscriptions: {active_subscriptions}")

    st.write("Subscription Plan Distribution:")
    plan_counts = df["plan_type"].value_counts()
    st.bar_chart(plan_counts)

# Fungsi untuk melihat langganan yang akan berakhir dalam 7 hari
def view_subscriptions_ending_soon(df):
    st.subheader("Subscriptions Ending Soon")
    if df.empty:
        st.warning("No subscription data available.")
        return

    today = datetime.datetime.now()
    next_week = today + datetime.timedelta(days=7)
    ending_soon = df[(df["is_active"]) & (pd.to_datetime(df["end_date"]) <= next_week)]

    if ending_soon.empty:
        st.info("No subscriptions ending within the next 7 days.")
    else:
        st.write(ending_soon)

# Fungsi utama
def main():
    st.title("Advanced Subscription Management System")

    df = load_data()
    users = load_users()

    if "is_logged_in" not in st.session_state:
        st.session_state.is_logged_in = False
        st.session_state.user_name = None
        st.session_state.role = None

    if not st.session_state.is_logged_in:
        st.subheader("Authentication")
        auth_mode = st.radio("Choose mode:", ["Login", "Register"])

        user_name = st.text_input("User  Name:")
        password = st.text_input("Password:", type="password")

        if auth_mode == "Register":
            role = st.radio("Role:", ["User ", "Admin"])
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

        if st.button("Logout"):
            st.session_state.is_logged_in = False
            st.session_state.user_name = None
            st.session_state.role = None
            st.success("You have been logged out.")

        if st.session_state.role == "User ":
            user_name = st.session_state.user_name
            
            st.subheader("User  Dashboard")
            action = st.selectbox("Choose an action:", ["Check Subscription Status", "Update Subscription", "Cancel Subscription"])

            if action == "Check Subscription Status":
                if user_name in df["user_name"].values:
                    subscription = df[df["user_name"] == user_name]
                    st.write(subscription)
                else:
                    st.warning("No subscription found for this user.")

            elif action == "Update Subscription":
                new_plan = st.selectbox("Select new plan:", ["monthly", "yearly"])
                if st.button("Update Subscription"):
                    success = update_subscription(df, user_name, new_plan)
                    if success:
                        st.success("Subscription updated successfully.")
                    else:
                        st.error("Failed to update subscription.")

            elif action == "Cancel Subscription":
                if st.button("Cancel Subscription"):
                    success = cancel_subscription(df, user_name)
                    if success:
                        st.success("Subscription cancelled successfully.")
                    else:
                        st.error("Failed to cancel subscription.")

        elif st.session_state.role == "Admin":
            st.subheader("Admin Dashboard")
            admin_action = st.selectbox("Choose an admin action:", ["Analyze Subscription Data", "View Subscriptions Ending Soon"])

            if admin_action == "Analyze Subscription Data":
                analyze_data(df)

            elif admin_action == "View Subscriptions Ending Soon":
                view_subscriptions_ending_soon(df)

if __name__ == "__main__":
    main()
