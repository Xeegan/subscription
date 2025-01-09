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
        return pd.DataFrame(columns=["id", "user_name", "plan_type", "start_date", "end_date", "is_active"])

# Fungsi untuk menyimpan data ke dalam dataset
def save_data(df):
    df.to_csv("subscriptions.csv", index=False)

# Fungsi untuk memeriksa status langganan
def check_status(row):
    today = datetime.datetime.now()
    end_date = datetime.datetime.strptime(row["end_date"], "%Y-%m-%d")
    if today > end_date:
        return False
    return True

# Fungsi untuk memperbarui langganan
def update_subscription(df, user_name, new_plan):
    user_data = df[df["user_name"] == user_name]
    if not user_data.empty:
        user_data["plan_type"] = new_plan
        user_data["end_date"] = (datetime.datetime.now() + datetime.timedelta(days=30) if new_plan == "monthly" 
                                  else datetime.datetime.now() + datetime.timedelta(days=365)).strftime("%Y-%m-%d")
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

def main():
    st.title("Subscription Management System with Dataset")

    # Load data dari file CSV
    df = load_data()

    # Input pengguna
    user_name = st.text_input("Enter your name:")

    if user_name:
        # Mengecek apakah pengguna sudah terdaftar
        user_data = df[df["user_name"] == user_name]

        if not user_data.empty:
            # Menampilkan status langganan pengguna
            user_row = user_data.iloc[0]
            st.write(f"Subscription for {user_name} is {'active' if user_row['is_active'] else 'inactive'} until {user_row['end_date']}.")
            
            # Cek status langganan
            if not check_status(user_row):
                st.error(f"Your subscription has expired on {user_row['end_date']}. Please renew or change your plan.")
            
            # Pilihan untuk mengubah paket
            new_plan = st.radio("Change your plan to:", ("monthly", "yearly"))
            if st.button(f"Change to {new_plan} plan"):
                if update_subscription(df, user_name, new_plan):
                    st.success(f"Subscription plan for {user_name} updated to {new_plan}.")
                else:
                    st.error(f"Failed to update the subscription for {user_name}.")
            
            # Pembatalan langganan
            if st.button("Cancel Subscription"):
                if cancel_subscription(df, user_name):
                    st.success(f"Subscription for {user_name} has been cancelled.")
                else:
                    st.error(f"Failed to cancel the subscription for {user_name}.")
        
        else:
            st.warning(f"No active subscription found for {user_name}.")
            
            # Membuat langganan baru
            plan_type = st.radio("Choose your plan type:", ("monthly", "yearly"))
            if st.button("Create Subscription"):
                new_id = len(df) + 1
                new_start_date = datetime.datetime.now().strftime("%Y-%m-%d")
                new_end_date = (datetime.datetime.now() + datetime.timedelta(days=30) if plan_type == "monthly"
                                else datetime.datetime.now() + datetime.timedelta(days=365)).strftime("%Y-%m-%d")
                new_subscription = pd.DataFrame({
                    "id": [new_id],
                    "user_name": [user_name],
                    "plan_type": [plan_type],
                    "start_date": [new_start_date],
                    "end_date": [new_end_date],
                    "is_active": [True]
                })
                df = pd.concat([df, new_subscription], ignore_index=True)
                save_data(df)
                st.success(f"New subscription created for {user_name} with {plan_type} plan.")
        st.write(df)

if __name__ == "__main__":
    main()
