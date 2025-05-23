from flask import request, make_response
from functools import wraps
import mysql.connector
import re
import os
import uuid

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from icecream import ic
ic.configureOutput(prefix=f'***** | ', includeContext=True)

UNSPLASH_ACCESS_KEY = 'YOUR_KEY_HERE'
ADMIN_ROLE_PK = "16fd2706-8baf-433b-82eb-8c7fada847da"
CUSTOMER_ROLE_PK = "c56a4180-65aa-42ec-a945-5fd21dec0538"
PARTNER_ROLE_PK = "f47ac10b-58cc-4372-a567-0e02b2c3d479"
RESTAURANT_ROLE_PK = "9f8c8d22-5a67-4b6c-89d7-58f8b8cb4e15"


# form to get data from input fields
# args to get data from the url
# values to get data from the url and from the form

class CustomException(Exception):
    def __init__(self, message, code):
        super().__init__(message)  # Initialize the base class with the message
        self.message = message  # Store additional information (e.g., error code)
        self.code = code  # Store additional information (e.g., error code)

def raise_custom_exception(error, status_code):
    raise CustomException(error, status_code)


##############################
def db():
    db = mysql.connector.connect(
        host="mysql",      # Replace with your MySQL server's address or docker service name "mysql"
        user="root",  # Replace with your MySQL username
        password="password",  # Replace with your MySQL password
        database="company"   # Replace with your MySQL database name
    )
    cursor = db.cursor(dictionary=True)
    return db, cursor


##############################
def no_cache(view):
    @wraps(view)
    def no_cache_view(*args, **kwargs):
        response = make_response(view(*args, **kwargs))
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response
    return no_cache_view


##############################

def allow_origin(origin="*"):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Call the wrapped function
            response = make_response(f(*args, **kwargs))
            # Add Access-Control-Allow-Origin header to the response
            response.headers["Access-Control-Allow-Origin"] = origin
            # Optionally allow other methods and headers for full CORS support
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS, PUT, DELETE"
            response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
            return response
        return decorated_function
    return decorator


##############################
USER_NAME_MIN = 2
USER_NAME_MAX = 20
USER_NAME_REGEX = f"^.{{{USER_NAME_MIN},{USER_NAME_MAX}}}$"
def validate_user_name():
    error = f"name {USER_NAME_MIN} to {USER_NAME_MAX} characters"
    user_name = request.form.get("user_name", "").strip()
    if not re.match(USER_NAME_REGEX, user_name): raise_custom_exception(error, 400)
    return user_name

##############################
USER_LAST_NAME_MIN = 2
USER_LAST_NAME_MAX = 20
USER_LAST_NAME_REGEX = f"^.{{{USER_LAST_NAME_MIN},{USER_LAST_NAME_MAX}}}$"
def validate_user_last_name():
    error = f"last name {USER_LAST_NAME_MIN} to {USER_LAST_NAME_MAX} characters"
    user_last_name = request.form.get("user_last_name", "").strip() # None
    if not re.match(USER_LAST_NAME_REGEX, user_last_name): raise_custom_exception(error, 400)
    return user_last_name

##############################
REGEX_EMAIL = "^(([^<>()[\]\\.,;:\s@\"]+(\.[^<>()[\]\\.,;:\s@\"]+)*)|(\".+\"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$"
def validate_user_email():
    error = "email invalid"
    user_email = request.form.get("user_email", "").strip()
    if not re.match(REGEX_EMAIL, user_email): raise_custom_exception(error, 400)
    return user_email

##############################
USER_PASSWORD_MIN = 8
USER_PASSWORD_MAX = 50
REGEX_USER_PASSWORD = f"^.{{{USER_PASSWORD_MIN},{USER_PASSWORD_MAX}}}$"
def validate_user_password():
    error = f"password {USER_PASSWORD_MIN} to {USER_PASSWORD_MAX} characters"
    user_password = request.form.get("user_password", "").strip()
    if not re.match(REGEX_USER_PASSWORD, user_password): raise_custom_exception(error, 400)
    return user_password

##############################
REGEX_UUID4 = "^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"
def validate_uuid4(uuid4 = ""):
    error = f"invalid uuid4"
    if not uuid4:
        uuid4 = request.values.get("uuid4", "").strip()
    if not re.match(REGEX_UUID4, uuid4): raise_custom_exception(error, 400)
    return uuid4

##############################
UPLOAD_ITEM_FOLDER = './images'
ALLOWED_ITEM_FILE_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

def validate_item_image():
    if 'item_file' not in request.files: raise_custom_exception("item_file missing", 400)
    file = request.files.get("item_file", "")
    if file.filename == "": raise_custom_exception("item_file name invalid", 400)

    if file:
        ic(file.filename)
        file_extension = os.path.splitext(file.filename)[1][1:]
        ic(file_extension)
        if file_extension not in ALLOWED_ITEM_FILE_EXTENSIONS: raise_custom_exception("item_file invalid extension", 400)
        filename = str(uuid.uuid4()) + file_extension
        return file, filename 

##############################
def validate_user_role():
    error = "Invalid role selected."
    user_role = request.form.get("user_role", "").strip().lower()
    allowed_roles = ["admin", "customer", "restaurant", "partner"]
    if user_role not in allowed_roles:
        raise_custom_exception(error, 400)
    return user_role

def get_role_pk(role_name):
    db_conn, cursor = db()
    try:
        q = "SELECT role_pk FROM roles WHERE role_name = %s"
        cursor.execute(q, (role_name,))
        row = cursor.fetchone()
        if not row:
            raise_custom_exception("Selected role does not exist.", 400)
        return row["role_pk"]
    finally:
        cursor.close()
        db_conn.close()

##############################
def send_verify_email(to_email, user_verification_key):
    try:
        # Create a gmail fullflaskdemomail
        # Enable (turn on) 2 step verification/factor in the google account manager
        # Visit: https://myaccount.google.com/apppasswords


        # Email and password of the sender's Gmail account
        sender_email = "kealearningwebdev@gmail.com"
        password = "pjzr vftl ejlt byid"  # If 2FA is on, use an App Password instead

        # Receiver email address
        receiver_email = to_email
        
        # Create the email message
        message = MIMEMultipart()
        message["From"] = "SPIS exam project 2024"
        message["To"] = receiver_email
        message["Subject"] = "Please verify your account"

        # Body of the email
        body = f"""To verify your account, please <a href="http://127.0.0.1/verify/{user_verification_key}">click here</a>"""
        message.attach(MIMEText(body, "html"))

        # Connect to Gmail's SMTP server and send the email
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()  # Upgrade the connection to secure
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message.as_string())
        print("Email sent successfully!")

        return "email sent"
       
    except Exception as ex:
        raise_custom_exception("cannot send email", 500)
    finally:
        pass


##############################
def send_forgot_password_email(to_email, user_verification_key):
    try:
        # Create a gmail fullflaskdemomail
        # Enable (turn on) 2 step verification/factor in the google account manager
        # Visit: https://myaccount.google.com/apppasswords


        # Email and password of the sender's Gmail account
        sender_email = "kealearningwebdev@gmail.com"
        password = "pjzr vftl ejlt byid"  # If 2FA is on, use an App Password instead

        # Receiver email address
        receiver_email = to_email
        
        # Create the email message
        message = MIMEMultipart()
        message["From"] = "SPIS exam project 2024"
        message["To"] = receiver_email
        message["Subject"] = "Reset your password here"

        # Body of the email
        body = f"""To reset your password, please <a href="http://127.0.0.1/change_password/{user_verification_key}">click here</a>"""
        message.attach(MIMEText(body, "html"))

        # Connect to Gmail's SMTP server and send the email
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()  # Upgrade the connection to secure
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message.as_string())
        print("Email sent successfully!")

        return "email sent"
    
    except Exception as ex:
        raise_custom_exception("cannot send email", 500)
    finally:
        pass

################

def send_buy_email(to_email, total_price, item_list):
    try:
        sender_email = "kealearningwebdev@gmail.com"
        password = "pjzr vftl ejlt byid"  # Use an App Password instead
        if not sender_email or not password:
            raise ValueError("Email configuration is missing.")

        receiver_email = to_email

        import html

        # Validate item_list
        if not isinstance(item_list, list):
            raise ValueError("item_list must be a list of dictionaries.")

        # Generate the HTML list
        item_list_html = "<ul>"
        for item in item_list:
            if isinstance(item, dict):
                print("Processing valid item:", item)
                item_title = html.escape(item.get('title', 'Unknown'))
                item_price = html.escape(str(item.get('price', '0')))
                item_list_html += f"""
                    <li>

                        {item_title} - {item_price} kr
                    </li>
                """
            else:
                print(f"Unexpected item structure: {item}")  # Log the unexpected item
        item_list_html += "</ul>"


        # Construct the email
        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = receiver_email
        message["Subject"] = "You have bought items, thank you for shopping at Spis!"

        # Body of the email
        body = f"""
        <p>Dear User,</p>
        <p>Here is a list of the items you have bought:</p>
        <div>
            {item_list_html}
        </div>
        <p>{total_price}</p>
        <p>If you did not perform this action, please contact our support team immediately.</p>
        <p>Best regards,<br>SPIS Exam Project 2024 Team</p>
        """
        message.attach(MIMEText(body, "html"))

        # Send the email
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message.as_string())
        print("Bought items email sent successfully!")

    except Exception as ex:
        print(f"Error: {ex}")
        raise ValueError("Cannot send buy items email.")

def send_deletion_info_email(user_email):  
    try:  
        sender_email = "kealearningwebdev@gmail.com"  
        password = "pjzr vftl ejlt byid"  # Use an App Password instead  
        if not sender_email or not password:  
            raise ValueError("Email configuration is missing.")  
          
          
                # Construct the email  
        message = MIMEMultipart()  
        message["From"] = sender_email  
        message["To"] = user_email  
        message["Subject"] = "Spis profile deleted succesfully"  
          
          
          
                # Body of the email  
        body = f"""  
        <p>Dear User</p>  
        <p>Your profile has been succefully deleted</p>  
        <p>Best regards,<br>SPIS Exam Project 2024 Team</p>  
        """  
        message.attach(MIMEText(body, "html"))  
          
          
        # Send the email  
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, password)  
            server.sendmail(sender_email, user_email, message.as_string())  
        ic("delete item email sent succesfully")  
  
    except Exception as ex:  
        print(f"Error: {ex}")  
        raise ValueError("Cannot send delete profile email.")
    
def send_block_email(to_email, item_title, item_price):
    try:
        sender_email = "kealearningwebdev@gmail.com"
        password = "pjzr vftl ejlt byid"  # Use an App Password instead
        if not sender_email or not password:
            raise ValueError("Email configuration is missing.")
 
        receiver_email = to_email
 
 
        # Construct the email
        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = receiver_email
        message["Subject"] = "One of your items has been blocked."
 
        # Body of the email
        body = f"""
        <p>Dear restaurant manager,</p>
        <p>One of your items has been blocked: {item_title}, with a price of {item_price}</p>
        <p>If you did not know about this, please contact our support team immediately.</p>
        <p>Best regards,<br>SPIS Exam Project 2024 Team</p>
        """
        message.attach(MIMEText(body, "html"))
 
        # Send the email
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message.as_string())
        print("Bought items email sent successfully!")
 
    except Exception as ex:
        print(f"Error: {ex}")
        raise ValueError("Cannot send buy items email.")