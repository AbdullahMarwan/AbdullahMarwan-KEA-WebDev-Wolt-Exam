from flask import Flask, session, render_template, redirect, url_for, make_response, request, flash
from flask_session import Session
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
import x
import uuid 
import time
import redis
import os

from icecream import ic
ic.configureOutput(prefix=f'***** | ', includeContext=True)

app = Flask(__name__)
app.config['SESSION_TYPE'] = 'filesystem'  # or 'redis', etc.
Session(app)

# Context Processor to Inject 'x' into All Templates
@app.context_processor
def inject_x():
    return dict(x=x)

# app.secret_key = "your_secret_key"

##############################
##############################
##############################

def _________GET_________(): pass

##############################
##############################

##############################
@app.get("/test-set-redis")
def view_test_set_redis():
    redis_host = "redis"
    redis_port = 6379
    redis_client = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)    
    redis_client.set("name", "Santiago", ex=10)
    # name = redis_client.get("name")
    return "name saved"

@app.get("/test-get-redis")
def view_test_get_redis():
    redis_host = "redis"
    redis_port = 6379
    redis_client = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)    
    name = redis_client.get("name")
    if not name: name = "no name"
    return name

##############################
@app.get("/")
def view_index():
    name = "X"
    return render_template("view_index.html", name=name)

##############################
@app.get("/signup")
@x.no_cache
def view_signup():  
    ic(session)
    if session.get("user"):
        if len(session.get("user").get("roles")) > 1:
            return redirect(url_for("view_choose_role")) 
        if "admin" in session.get("user").get("roles"):
            return redirect(url_for("view_admin"))
        if "customer" in session.get("user").get("roles"):
            return redirect(url_for("view_customer")) 
        if "partner" in session.get("user").get("roles"):
            return redirect(url_for("view_partner"))         
    return render_template("view_signup.html", x=x, title="Signup")


##############################
@app.get("/login")
@x.no_cache
def view_login():  
    # ic("#"*20, "VIEW_LOGIN")
    ic(session)
    # print(session, flush=True)  
    if session.get("user"):
        if len(session.get("user").get("roles")) > 1:
            return redirect(url_for("view_choose_role")) 
        if "admin" in session.get("user").get("roles"):
            return redirect(url_for("view_admin"))
        if "customer" in session.get("user").get("roles"):
            return redirect(url_for("view_customer")) 
        if "partner" in session.get("user").get("roles"):
            return redirect(url_for("view_partner"))         
    return render_template("view_login.html", x=x, title="Login", message=request.args.get("message", ""))


##############################
@app.get("/customer")
@x.no_cache
def view_customer():
    if not session.get("user", ""): 
        return redirect(url_for("view_login"))
    user = session.get("user")
    if len(user.get("roles", "")) > 1:
        return redirect(url_for("view_choose_role"))
    return render_template("view_customer.html", user=user)

##############################
@app.get("/partner")
@x.no_cache
def view_partner():
    if not session.get("user", ""): 
        return redirect(url_for("view_login"))
    
    user = session.get("user")
    
    # Ensure the user has only the 'partner' role
    if len(user.get("roles", [])) > 1:
        return redirect(url_for("view_choose_role"))
    if "partner" not in user.get("roles", []):
        return redirect(url_for("view_login"))  # Optional: Redirect if user lacks 'partner' role
    
    # Render the partner dashboard/profile template
    return render_template("view_partner.html", user=user)

##############################
@app.get("/admin")
@x.no_cache
def view_admin():
    if not session.get("user", ""): 
        return redirect(url_for("view_login"))
    user = session.get("user")
    if not "admin" in user.get("roles", ""):
        return redirect(url_for("view_login"))
    return render_template("view_admin.html")



##############################
@app.get("/choose-role")
@x.no_cache
def view_choose_role():
    if not session.get("user", ""): 
        return redirect(url_for("view_login"))
    if not len(session.get("user").get("roles")) >= 2:
        return redirect(url_for("view_login"))
    user = session.get("user")
    return render_template("view_choose_role.html", user=user, title="Choose role")


##############################
##############################
##############################

def _________POST_________(): pass

##############################
##############################
##############################

@app.post("/logout")
def logout():
    session.pop("user", None)
    flash("You have been logged out.", "info")
    return redirect(url_for("view_login"))


##############################
@app.post("/users")
@x.no_cache
def signup():
    try:
        user_name = x.validate_user_name()
        user_last_name = x.validate_user_last_name()
        user_email = x.validate_user_email()
        user_password = x.validate_user_password()
        user_role = x.validate_user_role()  # Validate and retrieve the selected role
        hashed_password = generate_password_hash(user_password)
        
        user_pk = str(uuid.uuid4())
        user_avatar = ""
        user_created_at = int(time.time())
        user_deleted_at = 0
        user_blocked_at = 0
        user_updated_at = 0
        user_verified_at = 0
        user_verification_key = str(uuid.uuid4())
        user_selected_role = x.get_role_pk(user_role)  # Retrieve role_pk
        
        db, cursor = x.db()
        q = '''
            INSERT INTO users (
                user_pk, user_name, user_last_name, user_email, 
                user_password, user_created_at, user_deleted_at, user_blocked_at, 
                user_updated_at, user_avatar, user_verified_at, 
                user_verification_key, user_selected_role
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        '''
        cursor.execute(q, (
            user_pk, user_name, user_last_name, user_email, 
            hashed_password, user_created_at, user_deleted_at, user_blocked_at, 
            user_updated_at, user_avatar, user_verified_at, 
            user_verification_key, user_selected_role
        ))
        
        x.send_verify_email(to_email=user_email, 
                            user_verification_key=user_verification_key)
        db.commit()
    
        return """<template mix-redirect="/login"></template>""", 201
    
    except Exception as ex:
        ic(ex)
        if "db" in locals(): db.rollback()
        if isinstance(ex, x.CustomException): 
            toast = render_template("___toast.html", message=ex.message)
            return f"""<template mix-target="#toast" mix-bottom>{toast}</template>""", ex.code    
        if isinstance(ex, x.mysql.connector.Error):
            ic(ex)
            if "users.user_email" in str(ex): 
                toast = render_template("___toast.html", message="Email not available")
                return f"""<template mix-target="#toast" mix-bottom>{toast}</template>""", 400
            return f"""<template mix-target="#toast" mix-bottom>System upgrading</template>""", 500        
        return f"""<template mix-target="#toast" mix-bottom>System under maintenance</template>""", 500    
    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()

##############################
@app.post("/login")
def login():
    try:

        user_email = x.validate_user_email()
        user_password = x.validate_user_password()

        db, cursor = x.db()
        q = """
            SELECT * FROM users 
            JOIN users_roles 
            ON user_pk = user_role_user_pk
            JOIN roles
            ON role_pk = user_role_role_fk
            WHERE user_email = %s AND user_deleted_at = 0 AND user_verified_at > 0
        """
        cursor.execute(q, (user_email,))
        rows = cursor.fetchall()
        if not rows:
            toast = render_template("___toast.html", message="User not registered, deleted, or not verified.")
            return f"""<template mix-target="#toast">{toast}</template>""", 400     
        if not check_password_hash(rows[0]["user_password"], user_password):
            toast = render_template("___toast.html", message="Invalid credentials.")
            return f"""<template mix-target="#toast">{toast}</template>""", 401
        roles = []
        for row in rows:
            roles.append(row["role_name"])
        user = {
            "user_pk": rows[0]["user_pk"],
            "user_name": rows[0]["user_name"],
            "user_last_name": rows[0]["user_last_name"],
            "user_email": rows[0]["user_email"],
            "roles": roles
        }
        ic(user)
        session["user"] = user
        if len(roles) == 1:
            return f"""<template mix-redirect="/{roles[0]}"></template>"""
        return f"""<template mix-redirect="/choose-role"></template>"""
    except Exception as ex:
        ic(ex)
        if "db" in locals(): db.rollback()
        if isinstance(ex, x.CustomException): 
            toast = render_template("___toast.html", message=ex.message)
            return f"""<template mix-target="#toast" mix-bottom>{toast}</template>""", ex.code    
        if isinstance(ex, x.mysql.connector.Error):
            ic(ex)
            return "<template>System upgrading</template>", 500        
        return "<template>System under maintenance</template>", 500  
    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()


##############################
@app.post("/items")
def create_item():
    try:
        # TODO: validate item_title, item_description, item_price
        file, item_image_name = x.validate_item_image()

        # Save the image
        file.save(os.path.join(x.UPLOAD_ITEM_FOLDER, item_image_name))
        # TODO: if saving the image went wrong, then rollback by going to the exception
        # TODO: Success, commit
        return item_image_name
    except Exception as ex:
        ic(ex)
        if "db" in locals(): db.rollback()
        if isinstance(ex, x.CustomException): 
            toast = render_template("___toast.html", message=ex.message)
            return f"""<template mix-target="#toast" mix-bottom>{toast}</template>""", ex.code    
        if isinstance(ex, x.mysql.connector.Error):
            ic(ex)
            return "<template>System upgrating</template>", 500        
        return "<template>System under maintenance</template>", 500  
    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()    


##############################
##############################
##############################

def _________PUT_________(): pass

##############################
##############################
##############################

@app.put("/users")
def user_update():
    try:
        if not session.get("user"): x.raise_custom_exception("please login", 401)

        user_pk = session.get("user").get("user_pk")
        user_name = x.validate_user_name()
        user_last_name = x.validate_user_last_name()
        user_email = x.validate_user_email()

        user_updated_at = int(time.time())

        db, cursor = x.db()
        q = """ UPDATE users
                SET user_name = %s, user_last_name = %s, user_email = %s, user_updated_at = %s
                WHERE user_pk = %s
            """
        cursor.execute(q, (user_name, user_last_name, user_email, user_updated_at, user_pk))
        if cursor.rowcount != 1: x.raise_custom_exception("cannot update user", 401)
        db.commit()
        return """<template>user updated</template>"""
    except Exception as ex:
        ic(ex)
        if "db" in locals(): db.rollback()
        if isinstance(ex, x.CustomException): return f"""<template mix-target="#toast" mix-bottom>{ex.message}</template>""", ex.code
        if isinstance(ex, x.mysql.connector.Error):
            if "users.user_email" in str(ex): return "<template>email not available</template>", 400
            return "<template>System upgrating</template>", 500        
        return "<template>System under maintenance</template>", 500    
    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()


##############################
@app.put("/users/block/<user_pk>")
def user_block(user_pk):
    try:        
        if not "admin" in session.get("user").get("roles"): return redirect(url_for("view_login"))
        user_pk = x.validate_uuid4(user_pk)
        user_blocked_at = int(time.time())
        db, cursor = x.db()
        q = 'UPDATE users SET user_blocked_at = %s WHERE user_pk = %s'
        cursor.execute(q, (user_blocked_at, user_pk))
        if cursor.rowcount != 1: x.raise_custom_exception("cannot block user", 400)
        db.commit()
        return """<template>user blocked</template>"""
    
    except Exception as ex:
        ic(ex)
        if "db" in locals(): db.rollback()
        if isinstance(ex, x.CustomException): 
            return f"""<template mix-target="#toast" mix-bottom>{ex.message}</template>""", ex.code        
        if isinstance(ex, x.mysql.connector.Error):
            ic(ex)
            return "<template>Database error</template>", 500        
        return "<template>System under maintenance</template>", 500  
    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()


##############################
@app.put("/users/unblock/<user_pk>")
def user_unblock(user_pk):
    try:
        if not "admin" in session.get("user").get("roles"): return redirect(url_for("view_login"))
        user_pk = x.validate_uuid4(user_pk)
        user_blocked_at = 0
        db, cursor = x.db()
        q = 'UPDATE users SET user_blocked_at = %s WHERE user_pk = %s'
        cursor.execute(q, (user_blocked_at, user_pk))
        if cursor.rowcount != 1: x.raise_custom_exception("cannot unblock user", 400)
        db.commit()
        return """<template>user unblocked</template>"""
    
    except Exception as ex:

        ic(ex)
        if "db" in locals(): db.rollback()
        if isinstance(ex, x.CustomException): 
            return f"""<template mix-target="#toast" mix-bottom>{ex.message}</template>""", ex.code        
        if isinstance(ex, x.mysql.connector.Error):
            ic(ex)
            return "<template>Database error</template>", 500        
        return "<template>System under maintenance</template>", 500  
    
    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()




##############################
##############################
##############################

def _________DELETE_________(): pass

##############################
##############################
##############################


@app.delete("/users/<user_pk>")
def user_delete(user_pk):
    try:
        # Check if user is logged
        if not session.get("user", ""): return redirect(url_for("view_login"))
        # Check if it is an admin
        if not "admin" in session.get("user").get("roles"): return redirect(url_for("view_login"))
        user_pk = x.validate_uuid4(user_pk)
        user_deleted_at = int(time.time())
        db, cursor = x.db()
        q = 'UPDATE users SET user_deleted_at = %s WHERE user_pk = %s'
        cursor.execute(q, (user_deleted_at, user_pk))
        if cursor.rowcount != 1: x.raise_custom_exception("cannot delete user", 400)
        db.commit()
        return """<template>user deleted</template>"""
    
    except Exception as ex:

        ic(ex)
        if "db" in locals(): db.rollback()
        if isinstance(ex, x.CustomException): 
            return f"""<template mix-target="#toast" mix-bottom>{ex.message}</template>""", ex.code        
        if isinstance(ex, x.mysql.connector.Error):
            ic(ex)
            return "<template>Database error</template>", 500        
        return "<template>System under maintenance</template>", 500  
    
    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()




##############################
##############################
##############################

def _________BRIDGE_________(): pass

##############################
##############################
##############################


##############################
@app.get("/verify/<verification_key>")
@x.no_cache
def verify_user(verification_key):
    try:
        ic(verification_key)
        verification_key = x.validate_uuid4(verification_key)
        user_verified_at = int(time.time())

        db, cursor = x.db()
        # Retrieve user details including user_selected_role
        q_select = '''
            SELECT user_pk, user_selected_role FROM users 
            WHERE user_verification_key = %s AND user_verified_at = 0
        '''
        cursor.execute(q_select, (verification_key,))
        user = cursor.fetchone()
        if not user:
            x.raise_custom_exception("Invalid or already verified verification key.", 400)
        
        user_pk = user["user_pk"]
        user_selected_role = user["user_selected_role"]

        # Update user_verified_at
        q_update = '''
            UPDATE users 
            SET user_verified_at = %s 
            WHERE user_pk = %s
        '''
        cursor.execute(q_update, (user_verified_at, user_pk))
        if cursor.rowcount != 1:
            x.raise_custom_exception("Cannot verify account.", 400)
        
        # Assign role in users_roles table
        q_insert_role = '''
            INSERT INTO users_roles (user_role_user_pk, user_role_role_fk)
            VALUES (%s, %s)
        '''
        cursor.execute(q_insert_role, (user_pk, user_selected_role))
        if cursor.rowcount != 1:
            x.raise_custom_exception("Cannot assign role to user.", 400)
        
        db.commit()
        return redirect(url_for("view_login", message="User verified and role assigned. Please login."))

    except Exception as ex:
        ic(ex)
        if "db" in locals(): db.rollback()
        if isinstance(ex, x.CustomException): 
            return f"""<template mix-target="#toast" mix-bottom>{ex.message}</template>""", ex.code    
        if isinstance(ex, x.mysql.connector.Error):
            ic(ex)
            return "Database under maintenance", 500        
        return "System under maintenance", 500  
    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()

####################
@app.get("/partner/edit_profile")
@x.no_cache
def view_edit_profile():
    if not session.get("user"): 
        return redirect(url_for("view_login"))
    user = session.get("user")
    return render_template("edit_profile.html", user=user, x=x)

@app.post("/partner/edit_profile")
@x.no_cache
def edit_profile():
    try:
        if not session.get("user"):
            return redirect(url_for("view_login"))
        
        user = session.get("user")
        user_pk = user.get("user_pk")

        # Validate input fields
        user_name = x.validate_user_name()
        user_last_name = x.validate_user_last_name()
        user_email = x.validate_user_email()

        user_updated_at = int(time.time())

        db, cursor = x.db()
        q = """
            UPDATE users
            SET user_name = %s, user_last_name = %s, user_email = %s, user_updated_at = %s
            WHERE user_pk = %s
        """
        cursor.execute(q, (user_name, user_last_name, user_email, user_updated_at, user_pk))
        if cursor.rowcount != 1:
            x.raise_custom_exception("Cannot update profile.", 400)
        
        db.commit()
        
        # Update session information
        user['user_name'] = user_name
        user['user_last_name'] = user_last_name
        user['user_email'] = user_email
        session['user'] = user

        flash("Profile updated successfully.", "success")
        return redirect(url_for("view_partner"))

    except Exception as ex:
        ic(ex)
        if "db" in locals():
            db.rollback()
        if isinstance(ex, x.CustomException):
            toast = render_template("___toast.html", message=ex.message, x=x)
            return f"""<template mix-target="#toast" mix-bottom>{toast}</template>""", ex.code
        if isinstance(ex, x.mysql.connector.Error):
            ic(ex)
            if "users.user_email" in str(ex):
                toast = render_template("___toast.html", message="Email not available.", x=x)
                return f"""<template mix-target="#toast" mix-bottom>{toast}</template>""", 400
            return f"""<template mix-target="#toast" mix-bottom>System upgrading.</template>""", 500        
        return f"""<template mix-target="#toast" mix-bottom>System under maintenance.</template>""", 500    
    finally:
        if "cursor" in locals():
            cursor.close()
        if "db" in locals():
            db.close()


######################
@app.get("/partner/delete_profile")
@x.no_cache
def view_delete_profile():
    if not session.get("user"):
        return redirect(url_for("view_login"))
    user = session.get("user")
    ic("Rendering delete_profile.html")
    return render_template("delete_profile.html", user=user)  # 'x' is injected via context processor


@app.post("/partner/request_delete_profile")
@x.no_cache
def request_delete_profile():
    try:
        ic("Request to delete profile received.")
        if not session.get("user"):
            ic("User not logged in. Redirecting to login.")
            # Optionally, flash a message here if desired
            flash("Please log in to delete your profile.", "warning")
            return redirect(url_for("view_login"))
        
        user = session.get("user")
        user_pk = user.get("user_pk")
        user_email = user.get("user_email")
        # printer user pk i terminalen
        ic(f"User PK: {user_pk}")

        # Verify password
        db, cursor = x.db()
        q = "SELECT user_password FROM users WHERE user_pk = %s AND user_deleted_at = 0"
        cursor.execute(q, (user_pk,))
        row = cursor.fetchone()
        ic(f"Database query result: {row}")
        if not row:
            x.raise_custom_exception("User not found or already deleted.", 400)
        
        if not check_password_hash(row["user_password"], user_password):
            x.raise_custom_exception("Invalid password.", 401)

        # Perform soft delete by setting user_deleted_at
        user_deleted_at = int(time.time())
        q_update = """
            UPDATE users
            SET user_deleted_at = %s
            WHERE user_pk = %s AND user_deleted_at = 0
        """
        cursor.execute(q_update, (user_deleted_at, user_pk))
        if cursor.rowcount != 1:
            x.raise_custom_exception("Cannot delete profile.", 400)
        
        db.commit()
        ic("User profile deleted successfully.")

        # Send informational email
        x.send_deletion_info_email(to_email=user_email)
        ic("Informational email about deletion sent.")

        # Clear session
        session.pop("user", None)
        ic("User session cleared.")

        # Return a redirect template to trigger frontend redirection
        return f"""<template mix-redirect="{url_for("view_login")}"></template>"""

    except Exception as ex:
        ic(f"Exception occurred during profile deletion: {ex}")
        if "db" in locals():
            db.rollback()
            ic("Database rolled back due to exception.")
        if isinstance(ex, x.CustomException):
            toast = render_template("___toast.html", message=ex.message)
            return f"""<template mix-target="#toast">{toast}</template>""", ex.code
        if isinstance(ex, x.mysql.connector.Error):
            ic(ex)
            return f"""<template mix-target="#toast" mix-bottom>Database error.</template>""", 500
        return f"""<template mix-target="#toast" mix-bottom>System under maintenance.</template>""", 500
    finally:
        if "cursor" in locals():
            cursor.close()
            ic("Cursor closed.")
        if "db" in locals():
            db.close()
            ic("Database connection closed.")

