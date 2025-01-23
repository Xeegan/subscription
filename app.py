import streamlit as st
import pandas as pd
import datetime
import hashlib
import altair as alt

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
        return pd.DataFrame(columns=["user_name", "password", "role", "email"])

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

# Fungsi untuk registrasi
def register_user(users, user_name, password, role, email):
    if user_name in users["user_name"].values:
        return False, "User already exists."

    hashed_password = hash_password(password)
    new_user = pd.DataFrame({
        "user_name": [user_name],
        "password": [hashed_password],
        "role": [role],
        "email": [email]
    })
    users = pd.concat([users, new_user], ignore_index=True)
    save_users(users)
    return True, "Registration successful."

# Fungsi untuk login
def login_user(users, user_name, password):
    hashed_password = hash_password(password)
    user = users[(users["user_name"] == user_name) & (users["password"] == hashed_password)]
    if not user.empty:
        return True, user.iloc[0]["role"]
    return False, None

# Fungsi untuk memeriksa status langganan
def check_status(row):
    today = datetime.datetime.now()
    end_date = datetime.datetime.strptime(row["end_date"], "%Y-%m-%d")
    if today > end_date:
        return False
    return True

# Fungsi untuk memperbarui langganan
def update_subscription(df, user_name, plan_type):
    try:
        today = datetime.datetime.now()
        new_end_date = (today + datetime.timedelta(days=30) if plan_type == "monthly" else today + datetime.timedelta(days=365)).strftime("%Y-%m-%d")
        df.loc[df["user_name"] == user_name, ["plan_type", "end_date", "is_active"]] = [plan_type, new_end_date, True]
        save_data(df)
        log_transaction(user_name, "update_subscription", f"Updated to {plan_type} plan")
        return True
    except Exception as e:
        st.error(f"Error updating subscription: {str(e)}")
        return False

# Fungsi untuk membatalkan langganan
def cancel_subscription(df, user_name):
    try:
        df.loc[df["user_name"] == user_name, "is_active"] = False
        save_data(df)
        log_transaction(user_name, "cancel_subscription", "Subscription cancelled")
        return True
    except Exception as e:
        st.error(f"Error cancelling subscription: {str(e)}")
        return False

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
    chart = alt.Chart(plan_counts.reset_index(), title="Plan Distribution").mark_bar().encode(
        x=alt.X("index", title="Plan Type"),
        y=alt.Y("plan_type", title="Count"),
        color=alt.Color("index", legend=None)
    )
    st.altair_chart(chart, use_container_width=True)

    # Analisis pendapatan
    plan_prices = {"monthly": 10, "yearly": 100}
    df["revenue"] = df["plan_type"].map(plan_prices)
    total_revenue = df["revenue"].sum()
    st.write(f"Total Revenue: ${total_revenue}")

    # Langganan yang segera kedaluwarsa
    today = datetime.datetime.now()
    df["days_until_expiry"] = pd.to_datetime(df["end_date"]) - today
    expiring_soon = df[df["days_until_expiry"] <= pd.Timedelta(days=7)]
    if not expiring_soon.empty:
        st.write("Subscriptions Expiring Soon:")
        st.write(expiring_soon[["user_name", "plan_type", "end_date"]])
    else:
        st.write("No subscriptions expiring within the next 7 days.")

# Fungsi utama aplikasi
def main():
    st.title("Complex Subscription Management System")

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
            email = st.text_input("Email:")
            role = st.radio("Role:", ["User", "Admin"])
            if st.button("Register"):
                success, message = register_user(users, user_name, password, role, email)
                if success:
                    st.success(message)
                else:
                    st.error(message)

        elif auth_mode == "Login":
            if st.button("Login"):
                success, role = login_user(users, user_name, password)
                if success:
                    st.session_state.is_logged_in = True
                    st.session_state.user_name = user_name
                    st.session_state.role = role
                    st.success(f"Welcome, {user_name}! Role: {role}")
                else:
                    st.error("Invalid username or password.")

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
                        "user_name": [user_name],
                        "plan_type": [plan_type],
                        "start_date": [new_start_date],
                        "end_date": [new_end_date],
                        "is_active": [True],
                        "role": ["User"]
                    })
                    df = pd.concat([df, new_subscription], ignore_index=True)
                    save_data(df)
                    log_transaction(user_name, "create_subscription", f"Created {plan_type} plan")
                    st.success(f"New subscription created for {user_name} with {plan_type} plan.")

        elif st.session_state.role == "Admin":
            st.subheader("Admin Panel")
            st.write(df)

            analyze_data(df)

            # Mengelola pengguna
            st.subheader("Manage Users")
            delete_user_name = st.text_input("Enter the name of the user to delete:")
            if st.button("Delete User"):
                if delete_user_name:
                    user_to_delete = df[df["user_name
