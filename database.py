import sqlite3
import hashlib

try:
    # Step 1: Connect to the SQLite database
    conn = sqlite3.connect('mydatabase.db')  # Connects or creates the database file
    cursor = conn.cursor()

    # Step 2: Create the table if it doesn't exist (with age, address, and password)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            age INTEGER,
            address TEXT,
            password TEXT
        )
    ''')
    conn.commit()

    # Step 3: Take user input for name, email, age, address, and password to insert a new user
    print("Please enter user details to add a new user:")
    name = input("Name: ")
    email = input("Email: ")
    age = input("Age: ")
    address = input("Address: ")
    password = input("Password: ")

    # Hash the password before inserting it into the database
    hashed_password = hashlib.sha256(password.encode()).hexdigest()

    # Step 4: Insert user input into the 'users' table
    try:
        cursor.execute('''
            INSERT INTO users (name, email, age, address, password) VALUES (?, ?, ?, ?, ?)
        ''', (name, email, age, address, hashed_password))
        conn.commit()
        print(f"User '{name}' with email '{email}', age '{age}', and address '{address}' added successfully!")
    except sqlite3.IntegrityError:
        print(f"Error: The email '{email}' is already in use.")

    # Step 5: Show all users in the database
    cursor.execute('SELECT * FROM users')
    rows = cursor.fetchall()

    print("\nAll users in the database:")
    for row in rows:
        print(row)

    # Step 6: Search for a user by name
    search_name = input("\nEnter a name to search: ")
    cursor.execute('''
        SELECT * FROM users WHERE name LIKE ?
    ''', ('%' + search_name + '%',))
    rows = cursor.fetchall()

    if rows:
        print(f"\nUsers found with name '{search_name}':")
        for row in rows:
            print(row)
    else:
        print(f"No users found with the name '{search_name}'.")

    # Step 7: Update user details (email, age, address)
    update_choice = input("\nWould you like to update a user's details? (y/n): ").lower()
    if update_choice == 'y':
        update_name = input("Enter the name of the user to update: ")
        new_email = input("Enter the new email: ")
        new_age = input("Enter the new age: ")
        new_address = input("Enter the new address: ")

        cursor.execute('''
            UPDATE users SET email = ?, age = ?, address = ? WHERE name = ?
        ''', (new_email, new_age, new_address, update_name))
        conn.commit()
        print(f"\nUser '{update_name}' updated successfully!")

    # Step 8: Delete a user
    delete_choice = input("\nWould you like to delete a user? (y/n): ").lower()
    if delete_choice == 'y':
        delete_name = input("Enter the name of the user to delete: ")

        cursor.execute('''
            DELETE FROM users WHERE name = ?
        ''', (delete_name,))
        conn.commit()
        print(f"\nUser '{delete_name}' deleted successfully!")

except sqlite3.DatabaseError as e:
    print(f"Database error occurred: {e}")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
finally:
    if conn:
        conn.close()
        print("\nDatabase connection closed.")

# Step 9: Search for users by email
def search_user_by_email(email):
    cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
    user = cursor.fetchone()
    if user:
        print(f"User found: {user}")
    else:
        print(f"No user found with email: {email}")
