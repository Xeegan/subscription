import streamlit as st
import datetime

# Kelas Subscription
class Subscription:
    def __init__(self, package, start_date, end_date):
        self.package = package
        self.start_date = start_date
        self.end_date = end_date
        self.status = "active"

    def renew(self):
        if self.package == "monthly":
            self.end_date = self.end_date + datetime.timedelta(days=30)
        elif self.package == "yearly":
            self.end_date = self.end_date + datetime.timedelta(days=365)
        self.status = "active"
        return f"Subscription renewed until {self.end_date}"

    def cancel(self):
        self.status = "cancelled"
        return "Subscription cancelled."

    def is_active(self):
        today = datetime.date.today()
        if today <= self.end_date and self.status == "active":
            return True
        return False

# Kelas User
class User:
    def __init__(self, name, email):
        self.name = name
        self.email = email
        self.subscription = None

    def subscribe(self, package):
        start_date = datetime.date.today()
        if package == "monthly":
            end_date = start_date + datetime.timedelta(days=30)
        elif package == "yearly":
            end_date = start_date + datetime.timedelta(days=365)
        self.subscription = Subscription(package, start_date, end_date)
        return f"{self.name} subscribed to {package} package from {start_date} to {end_date}"

    def check_subscription(self):
        if self.subscription and self.subscription.is_active():
            return f"Your {self.subscription.package} subscription is active until {self.subscription.end_date}."
        else:
            return "No active subscription or subscription has expired."

    def change_subscription(self, new_package):
        if self.subscription:
            self.subscription.cancel()
        return self.subscribe(new_package)

    def cancel_subscription(self):
        if self.subscription:
            self.subscription.cancel()
            return "Your subscription has been cancelled."

# Streamlit Interface
def main():
    st.title("Subscription Management System")

    # Form for user input
    name = st.text_input("Enter your name:")
    email = st.text_input("Enter your email:")
    action = st.selectbox("Choose an action", ["Subscribe", "Check Subscription", "Change Subscription", "Cancel Subscription"])

    # Initialize user instance
    if name and email:
        user = User(name, email)

    if action == "Subscribe":
        package = st.selectbox("Choose a subscription package", ["monthly", "yearly"])
        if st.button("Subscribe"):
            st.write(user.subscribe(package))

    elif action == "Check Subscription":
        if st.button("Check Subscription Status"):
            st.write(user.check_subscription())

    elif action == "Change Subscription":
        new_package = st.selectbox("Choose a new subscription package", ["monthly", "yearly"])
        if st.button("Change Subscription"):
            st.write(user.change_subscription(new_package))

    elif action == "Cancel Subscription":
        if st.button("Cancel Subscription"):
            st.write(user.cancel_subscription())

if __name__ == "__main__":
    main()
