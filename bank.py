import streamlit as st
from main import BankSystem

# PAGE CONFIG
st.set_page_config(
    page_title="Bank Management System",
    page_icon="🏦",
    layout="centered"
)

# CUSTOM CSS
st.markdown("""
<style>

.stApp {
    background: linear-gradient(to right, #0f172a, #1e293b);
    color: white;
}

.block-container {
    padding-top: 2rem;
}

.title {
    text-align: center;
    font-size: 42px;
    font-weight: bold;
    color: #38bdf8;
    margin-bottom: 10px;
}

.subtitle {
    text-align: center;
    color: #cbd5e1;
    margin-bottom: 30px;
}

.card {
    background-color: #1e293b;
    padding: 25px;
    border-radius: 18px;
    box-shadow: 0px 4px 20px rgba(0,0,0,0.3);
}

.balance-box {
    background-color: #0f766e;
    padding: 20px;
    border-radius: 15px;
    text-align: center;
    font-size: 28px;
    font-weight: bold;
    color: white;
    margin-top: 10px;
    margin-bottom: 10px;
}

</style>
""", unsafe_allow_html=True)

# BANK OBJECT
bank = BankSystem()

# SESSION STATE
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "account" not in st.session_state:
    st.session_state.account = None

if "pin" not in st.session_state:
    st.session_state.pin = None

# HEADER
st.markdown(
    '<div class="title">🏦 Banking Management System</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">Secure • Modern • Minimal Banking App</div>',
    unsafe_allow_html=True
)

# SIDEBAR
menu = st.sidebar.selectbox(
    "Navigation",
    [
        "Create Account",
        "Login",
        "Dashboard"
    ]
)

# CREATE ACCOUNT
if menu == "Create Account":

    st.markdown('<div class="card">', unsafe_allow_html=True)

    st.subheader("Create New Account")

    name = st.text_input("Account Holder Name")

    pin = st.text_input("4 Digit PIN", type="password")

    confirm_pin = st.text_input("Confirm PIN", type="password")

    if st.button("Create Account"):

        if not name:
            st.error("Name cannot be empty.")

        elif not pin.isdigit() or len(pin) != 4:
            st.error("PIN must be exactly 4 digits.")

        elif pin != confirm_pin:
            st.error("PINs do not match.")

        else:

            account = bank.create_account(name, pin)

            if account:

                st.success("Account Created Successfully!")

                st.info(
                    f"Your Account Number: {account.get_account_number()}"
                )

            else:
                st.error("Failed to create account.")

    st.markdown('</div>', unsafe_allow_html=True)

# LOGIN
elif menu == "Login":

    st.markdown('<div class="card">', unsafe_allow_html=True)

    st.subheader("Login to Account")

    account_number = st.text_input("Account Number")

    pin = st.text_input("PIN", type="password")

    if st.button("Login"):

        account = bank.read_account(account_number, pin)

        if account:

            st.session_state.logged_in = True
            st.session_state.account = account
            st.session_state.pin = pin

            st.success(f"Welcome {account.get_name()}!")

        else:
            st.error("Invalid Account Number or PIN.")

    st.markdown('</div>', unsafe_allow_html=True)

# DASHBOARD
elif menu == "Dashboard":

    if not st.session_state.logged_in:

        st.warning("Please login first.")

    else:

        account = st.session_state.account
        pin = st.session_state.pin

        st.markdown('<div class="card">', unsafe_allow_html=True)

        st.subheader("Account Dashboard")

        st.write(f"### 👤 Account Holder: {account.get_name()}")
        st.write(f"### 🆔 Account Number: {account.get_account_number()}")

        st.divider()

        # CHECK BALANCE
        st.subheader("Check Account Balance")

        if st.button("Check Balance"):

            balance = bank.get_account_balance(
                account.get_account_number(),
                pin
            )

            if balance is not None:

                st.markdown(
                    f"""
                    <div class="balance-box">
                        ₹ {balance:.2f}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            else:
                st.error("Unable to fetch balance.")

        st.divider()

        # DEPOSIT MONEY
        st.subheader("Deposit Money")

        deposit_amount = st.number_input(
            "Enter Deposit Amount",
            min_value=0.0,
            step=100.0,
            key="deposit"
        )

        if st.button("Deposit Money"):

            if deposit_amount <= 0:
                st.error("Please enter valid amount.")

            else:

                success = bank.deposit(
                    account.get_account_number(),
                    pin,
                    deposit_amount
                )

                if success:
                    st.success(
                        f"₹{deposit_amount:.2f} deposited successfully!"
                    )

                else:
                    st.error("Deposit failed.")

        st.divider()

        # WITHDRAW MONEY
        st.subheader("Withdraw Money")

        withdraw_amount = st.number_input(
            "Enter Withdraw Amount",
            min_value=0.0,
            step=100.0,
            key="withdraw"
        )

        if st.button("Withdraw Money"):

            if withdraw_amount <= 0:
                st.error("Please enter valid amount.")

            else:

                success = bank.withdraw(
                    account.get_account_number(),
                    pin,
                    withdraw_amount
                )

                if success:
                    st.success(
                        f"₹{withdraw_amount:.2f} withdrawn successfully!"
                    )

                else:
                    st.error("Insufficient balance or withdraw failed.")

        st.divider()

        # TRANSACTION HISTORY
        st.subheader("Transaction History")

        logs = bank.get_single_audit_logs(
            account.get_account_number()
        )

        if logs:

            for log in logs:

                st.info(
                    f"""
                    📌 Action: {log['action']}

                    💰 Amount: ₹{log['amount']:.2f}

                    🕒 Time: {log['timestamp']}
                    """
                )

        else:
            st.warning("No transaction history found.")

        st.divider()

        # UPDATE NAME
        st.subheader("Update Account Name")

        new_name = st.text_input("Enter New Name")

        if st.button("Update Name"):

            if not new_name:
                st.error("Name cannot be empty.")

            else:

                account.set_name(new_name)

                if bank.update_account(account):

                    st.success("Name updated successfully!")

                else:
                    st.error("Failed to update name.")

        st.divider()

        # CHANGE PIN
        st.subheader("Change PIN")

        old_pin = st.text_input(
            "Current PIN",
            type="password",
            key="old_pin"
        )

        new_pin = st.text_input(
            "New 4 Digit PIN",
            type="password",
            key="new_pin"
        )

        confirm_new_pin = st.text_input(
            "Confirm New PIN",
            type="password",
            key="confirm_new_pin"
        )

        if st.button("Change PIN"):

            if old_pin != pin:

                st.error("Current PIN incorrect.")

            elif not new_pin.isdigit() or len(new_pin) != 4:

                st.error("PIN must be exactly 4 digits.")

            elif new_pin != confirm_new_pin:

                st.error("PINs do not match.")

            else:

                account.set_pin_hash(new_pin)

                if bank.update_account(account):

                    st.session_state.pin = new_pin

                    st.success("PIN updated successfully!")

                else:
                    st.error("Failed to update PIN.")

        st.divider()

        # DELETE ACCOUNT
        st.subheader("Delete Account")

        if st.button("Delete Account"):

            success = bank.delete_account(
                account.get_account_number(),
                pin
            )

            if success:

                st.success("Account deleted successfully!")

                st.session_state.logged_in = False
                st.session_state.account = None
                st.session_state.pin = None

            else:
                st.error("Failed to delete account.")

        st.divider()

        # LOGOUT
        if st.button("Logout"):

            st.session_state.logged_in = False
            st.session_state.account = None
            st.session_state.pin = None

            st.success("Logged out successfully!")

        st.markdown('</div>', unsafe_allow_html=True)