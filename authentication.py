# authentication.py
from database import Session, User
import bcrypt
import socket
import random


def get_ip_address():
    """get the ip address"""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
    
        s.connect(("8.8.8.8", 80))
        IP = s.getsockname()[0]
    except Exception:
        IP = "127.0.0.1"
    finally:
        s.close()
    return IP


def assign_port():
   
    return random.randint(49152, 65535)


def register_user(username, password, ip_address):
    """Register a user and save their IP address and an assigned port."""
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    assigned_port = assign_port() 
    user = User(
        username=username,
        ip_address=ip_address,
        port=assigned_port,
        password_hash=hashed_password,
    )
    session = Session()
    existing_user = session.query(User).filter_by(username=username).first()
    if existing_user is not None:
        print(f"User {username} already exists.")
        session.close()
        return False
    try:
        session.add(user)
        session.commit()
        print(f"User {username} registered successfully with port {assigned_port}.")
        return True
    except Exception as e:
        print(f"An error occurred: {e}")
        session.rollback()
        return False
    finally:
        session.close()


def login_user(username, password):
    """Validate user's login credentials."""
    session = Session()
    user = session.query(User).filter_by(username=username).first()
    if user and bcrypt.checkpw(password.encode("utf-8"), user.password_hash):
        user.is_online = True  
        session.commit()
        session.close()
        return True
    session.close()
    return False


def update_user_ip(username):
    """Update the stored IP address for a user."""
    ip_address = get_ip_address()  # Automatically get the new IP address
    session = Session()
    user = session.query(User).filter_by(username=username).first()
    if user:
        user.ip_address = ip_address  # Update the user's IP address
        try:
            session.commit()  # Commit the changes to the database
            print(f"Updated IP address for {username} to {ip_address}")
            return True
        except Exception as e:
            print(f"An error occurred while updating IP address: {e}")
            session.rollback()  # Roll back in case of error
            return False
        finally:
            session.close()
    else:
        print(f"User {username} not found.")
        session.close()
        return False
