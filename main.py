import hashlib
import random
import string
from database import connect_to_database


# ENCRYPT and VERIFY PIN
def __hash_pin(pin):
    return hashlib.sha256(pin.encode()).hexdigest()


def __verify_pin(input_pin, stored_hashed_pin):
    return __hash_pin(input_pin) == stored_hashed_pin


# DATABASE and TABLE INITIALIZATION
def initilize_tables():

    connection = connect_to_database()

    if not connection:
        return False

    try:

        cursor = connection.cursor()

        create_accounts_tables = """
        CREATE TABLE IF NOT EXISTS accounts (
            account_number VARCHAR(50) PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            pin VARCHAR(255) NOT NULL,
            balance DECIMAL(15, 2) DEFAULT 0.00,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """

        create_audit_tables = """
        CREATE TABLE IF NOT EXISTS audit (
            id SERIAL PRIMARY KEY,
            account_number VARCHAR(50),
            holder_name VARCHAR(100),
            action VARCHAR(100) NOT NULL,
            amount DECIMAL(15, 2) DEFAULT 0.00,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (account_number)
            REFERENCES accounts(account_number)
            ON DELETE CASCADE
        );
        """

        cursor.execute(create_accounts_tables)
        cursor.execute(create_audit_tables)

        connection.commit()

        cursor.close()
        connection.close()

        print("Tables initialized successfully!")

        return True

    except Exception as error:

        print(f"Error in initializing tables: {error}")

        return False


class Account:

    def __init__(self, account_number="", name="", pin="", balance=0.00):

        self.__account_number = (
            account_number if account_number else self.__generate_account_number()
        )

        self.__name = name

        self.__pin = globals()['__hash_pin'](pin) if pin else None

        self.__balance = float(balance)

    @staticmethod
    def __generate_account_number():

        return ''.join(
            random.choices(
                string.ascii_uppercase + string.digits,
                k=10
            )
        )

    # GETTERS
    def get_account_number(self):
        return self.__account_number

    def get_name(self):
        return self.__name

    def get_balance(self):
        return self.__balance

    def get_pin_hash(self):
        return self.__pin

    # SETTERS
    def set_name(self, name):
        self.__name = name

    def set_pin_hash(self, pin):
        self.__pin = globals()['__hash_pin'](pin)

    def set_balance(self, balance):
        self.__balance = float(balance)

    # UTILITY METHODS
    def deposit(self, amount):

        if amount > 0:
            self.__balance += amount
            return True

        return False

    def withdraw(self, amount):

        if 0 < amount <= self.__balance:
            self.__balance -= amount
            return True

        return False

    # DATABASE CRUD OPERATIONS
    @classmethod
    def load_from_db(cls, account_number, pin):

        connection = connect_to_database()

        if not connection:
            return None

        try:

            cursor = connection.cursor()

            cursor.execute(
                """
                SELECT account_number, name, pin, balance
                FROM accounts
                WHERE account_number = %s
                """,
                (account_number,)
            )

            result = cursor.fetchone()

            cursor.close()
            connection.close()

            if result:

                stored_pin_hash = result[2]

                if globals()['__verify_pin'](pin, stored_pin_hash):

                    account = cls(
                        result[0],
                        result[1],
                        "",
                        float(result[3])
                    )

                    account._Account__pin = stored_pin_hash

                    return account

            return None

        except Exception as error:

            print(f"Error loading account from database: {error}")

            return None

    def save_to_db(self):

        connection = connect_to_database()

        if not connection:
            return False

        try:

            cursor = connection.cursor()

            cursor.execute(
                """
                INSERT INTO accounts
                (account_number, name, pin, balance)

                VALUES (%s, %s, %s, %s)

                ON CONFLICT (account_number)

                DO UPDATE SET
                    name = EXCLUDED.name,
                    pin = EXCLUDED.pin,
                    balance = EXCLUDED.balance
                """,
                (
                    self.__account_number,
                    self.__name,
                    self.__pin,
                    self.__balance
                )
            )

            connection.commit()

            print("Account saved successfully!")

            cursor.close()
            connection.close()

            return True

        except Exception as error:

            print(f"Error saving account to database: {error}")

            return False

    def delete_from_db(self):

        connection = connect_to_database()

        if not connection:
            return False

        try:

            cursor = connection.cursor()

            cursor.execute(
                """
                DELETE FROM accounts
                WHERE account_number = %s
                """,
                (self.__account_number,)
            )

            connection.commit()

            cursor.close()
            connection.close()

            return True

        except Exception as error:

            print(f"Error deleting account from database: {error}")

            return False


class Audit:

    @staticmethod
    def log_action(account_number, holder_name, action, amount=0.00):

        connection = connect_to_database()

        if not connection:
            return False

        try:

            cursor = connection.cursor()

            cursor.execute(
                """
                INSERT INTO audit
                (account_number, holder_name, action, amount)

                VALUES (%s, %s, %s, %s)
                """,
                (
                    account_number,
                    holder_name,
                    action,
                    amount
                )
            )

            connection.commit()

            cursor.close()
            connection.close()

            return True

        except Exception as error:

            print(f"Error logging audit action: {error}")

            return False

    @staticmethod
    def get_single_audit_logs(account_number):

        connection = connect_to_database()

        if not connection:
            return []

        try:

            cursor = connection.cursor()

            cursor.execute(
                """
                SELECT id, holder_name, action, amount, timestamp
                FROM audit
                WHERE account_number = %s
                ORDER BY timestamp DESC
                """,
                (account_number,)
            )

            results = cursor.fetchall()

            cursor.close()
            connection.close()

            logs = []

            for row in results:

                log_entry = {
                    "id": row[0],
                    "holder_name": row[1],
                    "action": row[2],
                    "amount": float(row[3]),
                    "timestamp": row[4].isoformat()
                }

                logs.append(log_entry)

            return logs

        except Exception as error:

            print(f"Error retrieving audit logs: {error}")

            return []

    @staticmethod
    def get_all_audit_logs():

        connection = connect_to_database()

        if not connection:
            return []

        try:

            cursor = connection.cursor()

            cursor.execute(
                """
                SELECT id, account_number, holder_name,
                action, amount, timestamp

                FROM audit

                ORDER BY timestamp DESC
                """
            )

            results = cursor.fetchall()

            cursor.close()
            connection.close()

            logs = []

            for row in results:

                log_entry = {
                    "id": row[0],
                    "account_number": row[1],
                    "holder_name": row[2],
                    "action": row[3],
                    "amount": float(row[4]),
                    "timestamp": row[5].isoformat()
                }

                logs.append(log_entry)

            return logs

        except Exception as error:

            print(f"Error retrieving audit logs: {error}")

            return []

    @staticmethod
    def clear_single_audit_logs(account_number):

        connection = connect_to_database()

        if not connection:
            return False

        try:

            cursor = connection.cursor()

            cursor.execute(
                """
                DELETE FROM audit
                WHERE account_number = %s
                """,
                (account_number,)
            )

            connection.commit()

            cursor.close()
            connection.close()

            return True

        except Exception as error:

            print(f"Error clearing audit logs: {error}")

            return False

    @staticmethod
    def clear_all_audit_logs():

        connection = connect_to_database()

        if not connection:
            return False

        try:

            cursor = connection.cursor()

            cursor.execute("DELETE FROM audit")

            connection.commit()

            cursor.close()
            connection.close()

            return True

        except Exception as error:

            print(f"Error clearing all audit logs: {error}")

            return False


# BANK SYSTEM CLASS
class BankSystem:

    def __init__(self):
        initilize_tables()

    def create_account(self, name, pin):

        account = Account("", name, pin)

        if account.save_to_db():

            Audit.log_action(
                account.get_account_number(),
                account.get_name(),
                "Account Created",
                0.0
            )

            return account

        return None

    def read_account(self, account_number, pin):

        account = Account.load_from_db(account_number, pin)

        if account:

            Audit.log_action(
                account_number,
                account.get_name(),
                "Account Accessed",
                0.0
            )

            return account

        return None

    def update_account(self, account):
        return account.save_to_db()

    def delete_account(self, account_number, pin):

        account = Account.load_from_db(account_number, pin)

        if account:

            success = account.delete_from_db()

            if success:

                Audit.log_action(
                    account_number,
                    account.get_name(),
                    "Account Deleted",
                    0.0
                )

                return True

        return False

    def deposit(self, account_number, pin, amount):

        account = Account.load_from_db(account_number, pin)

        if account and account.deposit(amount):

            account.save_to_db()

            Audit.log_action(
                account_number,
                account.get_name(),
                "Amount Deposited",
                amount
            )

            return True

        return False

    def withdraw(self, account_number, pin, amount):

        account = Account.load_from_db(account_number, pin)

        if account and account.withdraw(amount):

            account.save_to_db()

            Audit.log_action(
                account_number,
                account.get_name(),
                "Amount Withdrawn",
                amount
            )

            return True

        return False

    def get_account_balance(self, account_number, pin):

        account = Account.load_from_db(account_number, pin)

        if account:

            Audit.log_action(
                account_number,
                account.get_name(),
                "Balance Checked",
                0.0
            )

            return account.get_balance()

        return None

    def get_single_audit_logs(self, account_number):
        return Audit.get_single_audit_logs(account_number)

    def get_all_audit_logs(self):
        return Audit.get_all_audit_logs()

    def clear_single_audit_logs(self, account_number):
        return Audit.clear_single_audit_logs(account_number)

    def clear_all_audit_logs(self):
        return Audit.clear_all_audit_logs()


# VALID AMOUNT INPUT
def get_valid_amount(message="Enter the amount: Rs"):

    while True:

        try:

            amount = float(input(message))

            if amount <= 0:
                print("Amount must be greater than zero.")
                continue

            return amount

        except ValueError:
            print("Invalid input. Please enter a valid amount.")


# CLI INTERFACE
def create_account_cli(bank):

    print("=" * 40)
    print("Create New Account")
    print("=" * 40)

    name = input("Enter Account Holder Name: ").strip()

    if not name:
        print("Name cannot be empty.")
        input("Press Enter to Continue ....")
        return

    pin = input("Enter 4-digit PIN: ").strip()

    if not pin.isdigit() or len(pin) != 4:
        print("Invalid PIN.")
        input("Press Enter to Continue ....")
        return

    confirm_pin = input("Confirm PIN: ").strip()

    if pin != confirm_pin:
        print("PINs do not match.")
        input("Press Enter to Continue ....")
        return

    account = bank.create_account(name, pin)

    if account:

        print("\nAccount created successfully!")
        print(f"Your Account Number is: {account.get_account_number()}")

    else:
        print("Failed to create account.")

    input("Press Enter to Continue ....")


# LOGGED FUNCTIONS
def check_balance_cli(bank, account, pin):

    print("=" * 40)
    print("Current Account Balance")
    print("=" * 40)

    balance = bank.get_account_balance(
        account.get_account_number(),
        pin
    )

    if balance is None:
        print("Error Checking balance, try again.")
    else:
        print(f"Your current balance is: Rs{balance:.2f}")

    input("Press Enter to Continue ....")


def deposit_money_cli(bank, account, pin):

    print("=" * 40)
    print("Deposit Money")
    print("=" * 40)

    amount = get_valid_amount(
        "Enter the amount to deposit: Rs"
    )

    if bank.deposit(
        account.get_account_number(),
        pin,
        amount
    ):

        print(
            f"Successfully deposited Rs{amount:.2f} to your account."
        )

        balance = bank.get_account_balance(
            account.get_account_number(),
            pin
        )

        if balance is not None:
            print(f"Your new balance is: Rs{balance:.2f}")

    else:
        print("Failed to deposit money. Please try again.")

    input("Press Enter to Continue ....")


def withdraw_money_cli(bank, account, pin):

    print("=" * 40)
    print("Withdraw Money")
    print("=" * 40)

    amount = get_valid_amount(
        "Enter the amount to withdraw: Rs"
    )

    if bank.withdraw(
        account.get_account_number(),
        pin,
        amount
    ):

        print(
            f"Successfully withdrew Rs{amount:.2f} from your account."
        )

        balance = bank.get_account_balance(
            account.get_account_number(),
            pin
        )

        if balance is not None:
            print(f"Your new balance is: Rs{balance:.2f}")

    else:
        print(
            "Failed to withdraw money. Please check your balance and try again."
        )

    input("Press Enter to Continue ....")


def transaction_history_cli(bank, account):

    print("=" * 40)
    print("Transaction History")
    print("=" * 40)

    logs = bank.get_single_audit_logs(
        account.get_account_number()
    )

    if logs:

        for log in logs:

            print(
                f"{log['timestamp']} - "
                f"{log['action']} - "
                f"Rs{log['amount']:.2f}"
            )

    else:
        print("No transaction history found.")

    input("Press Enter to Continue ....")


def update_account_info_cli(bank, account, pin):

    print("=" * 40)
    print("Update Account Information")
    print("=" * 40)

    new_name = input(
        "Enter new name (leave blank to keep current): "
    ).strip()

    if new_name:
        account.set_name(new_name)

    current_balance = bank.get_account_balance(
        account.get_account_number(),
        pin
    )

    account.set_balance(current_balance)

    if bank.update_account(account):

        Audit.log_action(
            account.get_account_number(),
            account.get_name(),
            "Account Information Updated",
            0.0
        )

        print("Account name updated successfully.")

    else:
        print("Failed to update account name.")

    input("Press Enter to Continue ....")


def change_pin_logout_cli(bank, account, pin):

    print("=" * 40)
    print("Change PIN and Logout")
    print("=" * 40)

    old_pin = input("Enter current PIN: ").strip()

    if old_pin != pin:

        print("Incorrect current PIN. Update failed.")
        input("Press Enter to Continue ....")

        return False

    new_pin = input("Enter new 4-digit PIN: ").strip()

    if not new_pin.isdigit() or len(new_pin) != 4:

        print("Invalid PIN. Update failed.")
        input("Press Enter to Continue ....")

        return False

    confirm_pin = input("Confirm new PIN: ").strip()

    if new_pin != confirm_pin:

        print("PINs do not match. Update failed.")
        input("Press Enter to Continue ....")

        return False

    account.set_pin_hash(new_pin)

    if bank.update_account(account):

        Audit.log_action(
            account.get_account_number(),
            account.get_name(),
            "PIN Updated and Logged Out",
            0.0
        )

        print("PIN updated successfully. Logging out...")

        input("Press Enter to Continue ....")

        return True

    else:

        print("Failed to update PIN. Please try again.")

        input("Press Enter to Continue ....")

        return False


def delete_account_cli(bank, account, pin):

    print("=" * 40)
    print("Delete Account")
    print("=" * 40)

    confirmation = input(
        "Are you sure you want to delete your account? (yes/no): "
    ).strip().lower()

    if confirmation == "yes":

        if bank.delete_account(
            account.get_account_number(),
            pin
        ):

            print("Account deleted successfully.")

            input("Press Enter to Continue ....")

            return True

        else:

            print("Failed to delete account. Please try again.")

            input("Press Enter to Continue ....")

            return False

    else:

        print("Account deletion cancelled.")

        input("Press Enter to Continue ....")

        return False


# LOGIN CLI INTERFACE
def login_account_cli(bank):

    print("=" * 40)
    print("Login to Account")
    print("=" * 40)

    account_number = input(
        "Enter Account Number: "
    ).strip()

    if not account_number:

        print("Account number cannot be empty.")
        input("Press Enter to Continue ....")

        return

    pin = input("Enter PIN: ").strip()

    account = bank.read_account(account_number, pin)

    if account:

        print(f"\nWelcome, {account.get_name()}!")

    else:

        print("Invalid account number or PIN.")

        input("Press Enter to Continue ....")

        return

    input("Press Enter to Continue ....")

    while True:

        print("=" * 40)
        print(f"WELCOME, {account.get_name()}!")
        print(f"Account Number: {account.get_account_number()}")
        print("=" * 40)

        print("1. Check Balance")
        print("2. Deposit Money")
        print("3. Withdraw Money")
        print("4. Transaction History")
        print("5. Update Account Info")
        print("6. Change PIN and Logout")
        print("7. Delete Account")
        print("8. Logout")

        print("=" * 40)

        choice = input(
            "Enter your choice (1-8): "
        ).strip()

        if choice == "1":

            check_balance_cli(bank, account, pin)

        elif choice == "2":

            deposit_money_cli(bank, account, pin)

        elif choice == "3":

            withdraw_money_cli(bank, account, pin)

        elif choice == "4":

            transaction_history_cli(bank, account)

        elif choice == "5":

            update_account_info_cli(bank, account, pin)

        elif choice == "6":

            if change_pin_logout_cli(bank, account, pin):
                break

        elif choice == "7":

            if delete_account_cli(bank, account, pin):
                break

        elif choice == "8":

            print("Logging out...")
            break

        else:

            print("Invalid choice.")

            input("Press Enter to Continue ....")


# MAIN MENU
def main_menu():

    bank = BankSystem()

    while True:

        print("=" * 40)
        print("Bank Management System")
        print("=" * 40)

        print("1. Create Account")
        print("2. Login Account")
        print("0. Exit")

        print("=" * 40)

        choice = input("Enter choice: ").strip()

        if choice == "1":

            create_account_cli(bank)

        elif choice == "2":

            login_account_cli(bank)

        elif choice == "0":

            print("Thank you for using the service.")
            break

        else:

            print("Invalid choice.")

            input("Press Enter to Continue ....")


if __name__ == "__main__":
    main_menu()
                           
    