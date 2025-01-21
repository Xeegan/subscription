import streamlit as st
import pandas as pd
import datetime

# Fungsi untuk membaca dataset langganan
def load_data():
    try:
        df = pd.read_csv("subscriptions.csv")
        return df
    except FileNotFoundError:
        # Jika file tidak ada, buat dataset kosong
        return pd.DataFrame(columns=["id", "user_name", "plan_type", "start_date", "end_date", "is_active", "role"])

# Fungsi untuk menyimpan data ke dalam dataset
def save_data(df):
    df.to_csv("subscriptions.csv", index=False)

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
        return True
    return False

# Fungsi untuk menghapus pengguna dari dataset (untuk admin)
def delete_user(df, user_name):
    df = df[df["user_name"] != user_name]
    save_data(df)
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

def main():
    st.title("Advanced Subscription Management System")

    # Load data dari file CSV
    df = load_data()

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
                    st.success(f"New subscription created for {user_name} with {plan_type} plan.")

    elif role == "Admin":
        st.subheader("Admin Panel")
        st.write(df)

        analyze_data(df)
        notify_expiring_subscriptions(df)

        delete_user_name = st.text_input("Enter the name of the user to delete:")
        if st.button("Delete User"):
            if delete_user_name:
                df = delete_user(df, delete_user_name)
                st.success(f"User {delete_user_name} has been deleted.")
            else:
                st.error("Please enter a valid user name to delete.")

if __name__ == "__main__":
    main()
