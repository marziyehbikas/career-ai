from database import SessionLocal
from models import User


def create_first_admin():
    db = SessionLocal()

    try:
        email = input("Enter the email of the user to make admin: ").strip()

        user = db.query(User).filter(
            User.email == email
        ).first()

        if not user:
            print("User not found.")
            return

        if user.role == "admin":
            print("This user is already an admin.")
            return

        user.role = "admin"

        db.commit()

        print(f"{user.email} is now an admin.")

    finally:
        db.close()


if __name__ == "__main__":
    create_first_admin()