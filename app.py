import streamlit as st
import pandas as pd
import datetime
import hashlib

# Fungsi untuk membaca dataset langganan
def load_data():
    try:
        df = pd.read_csv("subscriptions.csv")
        return df
    except FileNotFoundError:
        # Jika file tidak ada, buat dataset kosong
        return pd.DataFrame(columns=["id", "user_name", "plan_type", "start_date", "end_date", "is_active", "role"])

# Fungsi untuk membaca dataset transaksi
def load_transactions():
    try:
        df = pd.read_csv("transactions.csv")
        return df
    except FileNotFoundError:
        # Jika file tidak ada, buat dataset kosong
        return pd.DataFrame(columns=["id", "user_name", "action", "timestamp", "details"])

# Fungsi untuk menyimpan data ke dalam dataset
def save_data(df):
    df.to_csv("subscriptions.csv", index=False)

def save_transactions(df):
    df.to_csv("transactions.csv", index=False)

# Fungsi untuk mencatat transaksi
def log_transaction(user_name, action, details):
    transactions = load_transactions()
    new_transaction = pd.DataFrame({
        "id": [len(transactions) + 1],
        "user_name": [user_name],
        "action": [action],
        "timestamp": [datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
        "details": [details]
    })
    transactions = pd.concat([transactions, new_transaction], ignore_index=True)
    save_transactions(transactions)

# Fungsi untuk memeriksa status langganan
def check_status(row):
    today = datetime.datetime.now()
    end_date = datetime.datetime.strptime(row["end_date"], "%Y-%m-%d")
    return today <= end_date

# Fungsi untuk memperbarui langganan
def update_subscription(df, user_name, new_plan):
    user_data = df[df["user_name"] == user_name]
    if not user_data.empty:
        user_data["plan_type"] = new_plan
        user_data["end_date"] = (datetime.datetime.now() + datetime.timedelta(days=30) if new_plan == "monthly" \
                                  else datetime.datetime.now() + datetime.timedelta(days=365)).strftime("%Y-%m-%d")
        user_data["is_active"] = True
        df.update(user_data)
        save_data(df)
        log_transaction(user_name, "update_subscription", f"Plan updated to {new_plan}")
        return True
    return False

# Fungsi untuk membatalkan langganan
def cancel_subscription(df, user_name):
    user_data = df[df["user_name"] == user_name]
    if not user_data.empty:
        user_data["is_active"] = False
        user_data["end_date"] = datetime.datetime.now().strftime("%Y-%m-%d")
        df.update(user_data)
        save_data(df)
        log_transaction(user_name, "cancel_subscription", "Subscription cancelled")
        return True
    return False

# Fungsi untuk menghapus pengguna dari dataset (untuk admin)
def delete_user(df, user_name):
    df = df[df["user_name"] != user_name]
    save_data(df)
    log_transaction(user_name, "delete_user", "User deleted")
    return df

# Fungsi untuk analisis data statistik
def analyze_data(df):
    st.subheader("Subscription Analytics")
    total_users = len(df)
    active_users = len(df[df["is_active"] == True])
    inactive_users = total_users - active_users

    st.write(f"Total Users: {total_users}")
    st.write(f"Active Subscriptions: {active_users}")
    st.write(f"Inactive Subscriptions: {inactive_users}")

    st.bar_chart(df["plan_type"].value_counts())

# Fungsi untuk mengirim notifikasi status hampir habis
def notify_expiring_subscriptions(df):
    st.subheader("Expiring Subscriptions")
    today = datetime.datetime.now()
    expiring = df[df["end_date"].apply(lambda x: (datetime.datetime.strptime(x, "%Y-%m-%d") - today).days <= 7)]

    if not expiring.empty:
        st.write("The following subscriptions are about to expire in the next 7 days:")
        st.table(expiring)
    else:
        st.write("No subscriptions are expiring in the next 7 days.")

# Fungsi untuk membuat kode diskon
def create_discount_code(discount_codes, code, discount_percentage):
    discount_codes[code] = discount_percentage
    return discount_codes

# Fungsi untuk memvalidasi kode diskon
def validate_discount_code(discount_codes, code):
    return discount_codes.get(code, None)

def main():
    st.title("Advanced Subscription Management System")

    # Load data dari file CSV
    df = load_data()
    discount_codes = {}

    # Pilihan peran
    role = st.radio("Select your role:", ("User", "Admin"))

    if role == "User":
        user_name = st.text_input("Enter your name:")

        if user_name:
            user_data = df[df["user_name"] == user_name]

            if not user_data.empty:
                user_row = user_data.iloc[0]
                st.write(f"Subscription for {user_name} is {'active' if user_row['is_active'] else 'inactive'} until {user_row['end_date']}.")

                if not check_status(user_row):
                    st.error(f"Your subscription has expired on {user_row['end_date']}. Please renew or change your plan.")

                new_plan = st.radio("Change your plan to:", ("monthly", "yearly"))
                discount_code = st.text_input("Enter discount code (if any):")

                if st.button(f"Change to {new_plan} plan"):
                    discount = validate_discount_code(discount_codes, discount_code)
                    if discount:
                        st.success(f"Discount applied: {discount}%")
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

    elif role == "Admin":
        st.subheader("Admin Panel")
        st.write(df)

        analyze_data(df)
        notify_expiring_subscriptions(df)

        # Membuat kode diskon
        st.subheader("Manage Discount Codes")
        discount_code = st.text_input("Enter new discount code:")
        discount_percentage = st.number_input("Enter discount percentage:", min_value=0, max_value=100, step=1)
        if st.button("Create Discount Code"):
            discount_codes = create_discount_code(discount_codes, discount_code, discount_percentage)
            st.success(f"Discount code {discount_code} with {discount_percentage}% discount created.")

        delete_user_name = st.text_input("Enter the name of the user to delete:")
        if st.button("Delete User"):
            if delete_user_name:
                df = delete_user(df, delete_user_name)
                st.success(f"User {delete_user_name} has been deleted.")
            else:
                st.error("Please enter a valid user name to delete.")

if __name__ == "__main__":
    main()
