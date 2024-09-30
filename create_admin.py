from app import db, Admin, bcrypt, app

# Function to create an admin user
def create_admin():
    username = input("Enter the username for the admin: ")
    password = input("Enter the password for the admin: ")  # Consider using getpass for security

    # Start an application context
    with app.app_context():
        # Hash the password using bcrypt
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        # Create a new admin instance
        admin_user = Admin(username=username, password=hashed_password)

        # Add the admin to the session and commit to the database
        db.session.add(admin_user)
        db.session.commit()

        print("Admin user created successfully!")

if __name__ == "__main__":
    create_admin()
