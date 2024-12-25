# create_admin.py
from app import db, create_app
from app.models import User
from app.utils import hash_password  # Ensure this is available to hash passwords

# Initialize Flask application context
app = create_app()
app.app_context().push()

# Create the admin user if it doesn't exist
admin_email = "admin@gmail.com"  # Replace with a real admin email
existing_admin = User.query.filter_by(email=admin_email).first()

if not existing_admin:
    admin_user = User(
        email=admin_email,
        password=hash_password("admin123"),  # Replace with a strong password
        name="Admin",
        role="admin",
        address=" ",
        pin_code=" ",
        contact_no=" "
    )
    db.session.add(admin_user)
    db.session.commit()
    print("Admin user created successfully.")
else:
    print("Admin user already exists.")
