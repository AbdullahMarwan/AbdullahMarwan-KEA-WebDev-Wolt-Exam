import json
import random
from flask import Flask, session, render_template, redirect, url_for, make_response, request, flash, jsonify
from flask_session import Session
from datetime import datetime
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
import x
from werkzeug.utils import secure_filename
import uuid 
import time
import redis
import os
#
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

@app.route('/get_cart', methods=['GET'])
def get_cart():
    try:
        cart_data = session.get('cart', [])
        return jsonify({"cart": cart_data}), 200
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "Failed to fetch cart"}), 500



import threading

session_lock = threading.Lock()

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    try:
        new_cart_item = request.json.get("cart", [])
        
        if not (isinstance(new_cart_item, list) and all(isinstance(item, dict) for item in new_cart_item)):
            return jsonify({"error": "Invalid cart data format"}), 400

        with session_lock:
            existing_cart = session.get("cart", [])
            session["cart"] = existing_cart + new_cart_item
            session.modified = True
            session.permanent = True

        print("Updated cart:", session["cart"])
        
        return jsonify({"message": "Cart updated successfully", "cart": session["cart"]}), 200

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "Failed to update cart"}), 500




@app.route('/remove_from_cart', methods=['POST'])
def remove_from_cart():
    try:
        item_pk = request.json.get('pk')
        if not item_pk:
            return jsonify({"error": "Invalid item_pk provided"}), 400

        cart_data = session.get('cart', [])

        # Remove only the first occurrence of an item with the matching pk
        found = False
        updated_cart = []
        for item in cart_data:
            if not found and str(item['pk']) == str(item_pk):
                found = True  # Skip this item (remove it) and stop at the first match
                continue
            updated_cart.append(item)

        # Update the session with the modified cart
        session['cart'] = updated_cart
        session.modified = True

        return jsonify({"message": "Item removed successfully", "cart": updated_cart}), 200
    except Exception as e:
        print(f"Error in remove_from_cart: {e}")
        return jsonify({"error": "Failed to remove item"}), 500



##############################

@app.route('/buy_items', methods=['POST'])
def buy_items():
    try:
        data = request.json  # Parse incoming JSON
        total_price = data.get("totalPrice")
        item_list = data.get("itemList")
        user = session.get("user")
        user_email = user.get("user_email")


        ic("total_price:" + total_price)
        ic("Item list:", item_list)

        # Perform your logic here...

        # Send informational email
        x.send_buy_email(to_email=user_email, total_price=total_price, item_list=item_list)
        ic("buy email sent.")

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


##############################
def showRestaurantList():
    try:
        db, cursor = x.db()
        query = """
            SELECT users.user_pk, users.user_name
            FROM users
            JOIN users_roles ON users.user_pk = users_roles.user_role_user_fk
            WHERE users_roles.user_role_role_fk = '9f8c8d22-5a67-4b6c-89d7-58f8b8cb4e15'
        """
        cursor.execute(query)
        
        # Fetch all rows and structure the data into dictionaries
        restaurants = cursor.fetchall()
        # print("Results:", restaurants)  # Debugging output: Print the raw result from the query
        
        return restaurants
        # return restaurants
    except Exception as ex:
        print(f"Error fetching restaurants: {ex}")
        return []
    finally:
        if "cursor" in locals():
            cursor.close()
        if "db" in locals():
            db.close()

# Function to fetch items based on restaurant ID
def showItemListByRestaurant(restaurant_id):
    try:
        db, cursor = x.db()
        q = "SELECT * FROM `items` WHERE `item_user_fk` = %s"
        cursor.execute(q, (restaurant_id,))
        items = cursor.fetchall()
        print("Items fetched from database:", items)
        return items
    except Exception as ex:
        print(f"Error fetching items: {ex}")
        return []  # Return empty list in case of error
    finally:
        if "cursor" in locals():
            cursor.close()
        if "db" in locals():
            db.close()

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
        if "restaurant" in session.get("user").get("roles"):
            return redirect(url_for("view_restaurant"))         
    return render_template("view_signup.html", x=x, title="Signup")

##############################
@app.get("/forgot_password")
@x.no_cache
def view_forgot_password():     
    return render_template("view_forgot_password.html", x=x, title="ForgotPassword")


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
            return redirect(url_for("admin_or_pagination"))
        if "customer" in session.get("user").get("roles"):
            return redirect(url_for("view_customer")) 
        if "partner" in session.get("user").get("roles"):
            return redirect(url_for("view_partner"))     
        if "restaurant" in session.get("user").get("roles"):
            return redirect(url_for("view_restaurant"))    
    return render_template("view_login.html", x=x, title="Login", message=request.args.get("message", ""))

##############################
@app.get("/customer")
@x.no_cache
def view_customer():
    try:
        # Handle session and user authentication
        if not session.get("user", ""):
            return redirect(url_for("view_login"))
        user = session.get("user")
        if "customer" not in user.get("roles", ""):
            return redirect(url_for("view_login"))
        
        items = showItemList()  # Fetch items
        restaurants = showRestaurantList()  # Fetch restaurants
        
        return render_template("view_customer.html", items=items, restaurants = restaurants, user=user)
    except Exception as ex:
        print(f"Error in view_customer: {ex}")
        return "Error occurred", 500

    except Exception as ex:
        if isinstance(ex, x.mysql.connector.Error):
            return f"""<template mix-target="#toast" mix-bottom>Database error occurred.</template>""", 500
    
        return f"""<template mix-target="#toast" mix-bottom>System under maintenance.</template>""", 500
        
    finally:
        pass
    
############################## SEARCH FOR ITEM
@app.route("/api/search-items", methods=["GET"])
def api_search_items():
    try:
        query = request.args.get("q", "").strip()
        if not query:
            return {"items": []}
        db, cursor = x.db()
        q = "SELECT `item_title`, `item_price` FROM `items` WHERE `item_title` LIKE %s"
        cursor.execute(q, (f"%{query}%",))
        items = cursor.fetchall()

        return {"items": items}
    except Exception as ex:
        if isinstance(ex, x.mysql.connector.Error):
            return {"error": "Database error occurred."}, 500
        return {"error": "System under maintenance."}, 500
    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()

@app.get("/api/restaurants")
def get_restaurants():
    try:
        restaurants = showRestaurantList()
        
        def generate_random_coordinates():
            # Latitude range for Copenhagen (approx. 55.61 to 55.73)
            lat = random.uniform(55.61, 55.73)
            # Longitude range for Copenhagen (approx. 12.48 to 12.65)
            lon = random.uniform(12.48, 12.65)
            return lat, lon
        
        for restaurant in restaurants:
            lat, lon = generate_random_coordinates()
            restaurant['lat'] = lat
            restaurant['lon'] = lon
        
        return jsonify(restaurants)
    except Exception as ex:
        print(f"Error in get_restaurants: {ex}")
        return jsonify({"error": "Failed to fetch restaurants"}), 500

        return {"items": items}
    except Exception as ex:
        if isinstance(ex, x.mysql.connector.Error):
            return {"error": "Database error occurred."}, 500
        return {"error": "System under maintenance."}, 500
    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()

############################## SEARCH FOR RESTAURANT
@app.route("/api/search-restaurants", methods=["GET"])
def api_search_restaurants():
    try:
        query = request.args.get("q", "").strip()
        if not query:
            return {"restaurants": []}

        db, cursor = x.db()
        q = """
            SELECT u.user_name 
            FROM users u
            JOIN users_roles ur ON u.user_pk = ur.user_role_user_fk
            WHERE ur.user_role_role_fk = %s AND u.user_name LIKE %s
        """
        cursor.execute(q, ("9f8c8d22-5a67-4b6c-89d7-58f8b8cb4e15", f"%{query}%"))
        restaurants = cursor.fetchall()

        return {"restaurants": restaurants}
    except Exception as ex:
        if isinstance(ex, x.mysql.connector.Error):
            return {"error": "Database error occurred."}, 500
        return {"error": "System under maintenance."}, 500
    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()


############################### Route for viewing the restaurant (without items)

@app.get("/restaurant")
@x.no_cache
def view_restaurant():
    if not session.get("user", ""):
        return redirect(url_for("view_login"))
    
    user = session.get("user")
    if "restaurant" not in user.get("roles", {}):
        return redirect(url_for("view_login"))
    
    restaurant_id = user.get("user_pk")
    if not restaurant_id:
        return redirect(url_for("view_login"))
    
    # Render the restaurant page without items (initial state)
    return render_template("view_restaurant.html", user=user)

########################################################################### ITEMS FOR A SPECIFIC RESTAURANT CUSTOMER POV
# Route for viewing the restaurant items (when the button is clicked)
@app.route('/customer/items/<restaurant_id>')
def customer_items(restaurant_id):
    if not session.get("user", ""):
        return redirect(url_for("view_login"))

    user = session.get("user")
    if "customer" not in user.get("roles", {}):
        return redirect(url_for("view_login"))
    
    restaurants = showRestaurantList()
    
    print("Restaurant ID after clicking button:", restaurant_id)

    items = showItemListByRestaurant(restaurant_id)  # Fetch items based on restaurant_id
    
    # restaurant_name = request.args.get("restaurant_name").value
    
    # Fetch restaurant name using the user_pk (restaurant_id)
    restaurant_name = None
    for restaurant in restaurants:
        if restaurant['user_pk'] == restaurant_id:
            restaurant_name = restaurant['user_name']
            break
    
    return render_template('view_customer.html', items=items, restaurants=restaurants, user=user, restaurant_name=restaurant_name)

########################################################################### SHOW ALL ITEMS:

# Route for viewing the restaurant items (when the button is clicked)
@app.route('/restaurant/items/<restaurant_id>')
def restaurant_items(restaurant_id):
    if not session.get("user", ""):
        return redirect(url_for("view_login"))

    user = session.get("user")
    if "restaurant" not in user.get("roles", {}):
        return redirect(url_for("view_login"))
    
    print("Restaurant ID after clicking button:", restaurant_id)

    items = showItemListByRestaurant(restaurant_id)  # Fetch items based on restaurant_id
    return render_template('view_restaurant.html', view='items', items=items, user=user)

########################################################################### ADD NEW ITEM
@app.route('/restaurant/add_item', methods=['GET', 'POST'])
def restaurant_add_item():
    # Allowed image extensions (you can expand this if needed)
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

    # Function to check allowed file extension
    def allowed_file(filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    if not session.get("user", ""):
        return redirect(url_for("view_login"))

    user = session.get("user")
    if "restaurant" not in user.get("roles", {}):
        return redirect(url_for("view_login"))
    
    if request.method == 'POST':
        # Get form data (title, price, image)
        item_pk = str(uuid.uuid4())  # Generate unique item primary key
        item_user_fk = user.get("user_pk")
        item_title = request.form.get('item_title')
        item_price = request.form.get('item_price')
        item_image = request.files.get('item_image')

        # Check if the image exists and is allowed
        if item_image and allowed_file(item_image.filename):
            filename = secure_filename(item_image.filename)  # Secure the filename
            image_path = os.path.join('static', 'dishes', filename)  # Save inside the 'static/dishes' folder
            
            # Make sure the 'static/dishes' directory exists
            dishes_folder = os.path.join('static', 'dishes')
            if not os.path.exists(dishes_folder):
                os.makedirs(dishes_folder)  # Create 'dishes' directory if it doesn't exist
            
            # Save the file to the 'static/dishes' folder
            item_image.save(image_path)  # Save in 'static/dishes' folder
            
        else:
            image_path = None  # Handle case where image is not provided or not allowed

        # Now insert item details into the database
        db, cursor = x.db()

        q = '''
        INSERT INTO `items`(
            `item_pk`, `item_user_fk`, `item_title`, `item_price`, `item_image`
        ) VALUES (%s, %s, %s, %s, %s)
        '''
        cursor.execute(q, (
            item_pk, item_user_fk, item_title, item_price, filename if item_image else None
        ))

        
        db.commit()  # Commit changes to the database
        
        # After inserting, redirect to the items page to view all items
        return redirect(url_for('restaurant_items', restaurant_id=user.get('user_pk')))
    
    return render_template('view_restaurant.html', view='add_item', user=user)

########################################################################### RESTAURANT EDIT ITEM
@app.route('/restaurant/edit_item/<item_id>', methods=['GET', 'POST'])
def restaurant_edit_item(item_id):
    # Allowed image extensions (you can expand this if needed)
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

    # Function to check allowed file extension
    def allowed_file(filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    if not session.get("user", ""):
        return redirect(url_for("view_login"))

    user = session.get("user")
    if "restaurant" not in user.get("roles", {}):
        return redirect(url_for("view_login"))
    
    db, cursor = x.db()

    # Fetch the item from the database by its item_id
    cursor.execute("SELECT * FROM items WHERE item_pk = %s AND item_user_fk = %s", (item_id, user.get("user_pk")))
    item = cursor.fetchone()

    if not item:
        return redirect(url_for('restaurant_items', restaurant_id=user.get('user_pk')))  # Redirect if item not found
    
    if request.method == 'POST':
        # Handle form submission (updating item details)
        item_title = request.form.get('item_title')
        item_price = request.form.get('item_price')
        item_image = request.files.get('item_image')

        # Optional: process image upload if a new image is provided
        if item_image and allowed_file(item_image.filename):
            filename = secure_filename(item_image.filename)
            image_path = os.path.join('static', 'dishes', filename)  # Correct path for saving inside static/dishes
            
            # Make sure the 'static/dishes' directory exists
            dishes_folder = os.path.join('static', 'dishes')
            if not os.path.exists(dishes_folder):
                os.makedirs(dishes_folder)  # Create 'dishes' folder if it doesn't exist
            
            # Save the new image to 'static/dishes'
            item_image.save(image_path)
        else:
            image_path = item['item_image']  # Use existing image if no new image is provided

        # Update item details in the database, including the image path if it was updated
        cursor.execute(''' 
            UPDATE items 
            SET item_title = %s, item_price = %s, item_image = %s
            WHERE item_pk = %s
        ''', (item_title, item_price, filename if item_image else item['item_image'], item_id))

        db.commit()

        return redirect(url_for('restaurant_items', restaurant_id=user.get('user_pk')))

    # Render the edit item form
    return render_template('view_restaurant.html', view='edit_item', item=item, user=user)


################################################################################
@app.get("/partner")
@x.no_cache
def view_partner():
    # Handle session and user authentication
    if not session.get("user", ""):
        return redirect(url_for("view_login"))
    user = session.get("user")
    if "partner" not in user.get("roles", ""):
        return redirect(url_for("view_login"))
    
    user = session.get("user")
    
    # Render the partner dashboard/profile template
    return render_template("view_partner.html", user=user)

##############################
@app.get('/admin')
@app.get('/admin/page/<int:page_id>')
def admin_or_pagination(page_id=1):
    try:
        # Handle session and user authentication
        if not session.get("user", ""):
            return redirect(url_for("view_login"))
        user = session.get("user")
        if "admin" not in user.get("roles", ""):
            return redirect(url_for("view_login"))
        
        limit = 20 
        offset = (page_id - 1) * limit  # Offset is based on the page_id
        
        # Database query for users
        db, cursor = x.db()
        q = "SELECT `user_pk`, `user_name`, `user_last_name`, `user_avatar`, `user_email`, `user_deleted_at`, `user_blocked_at`, `user_verified_at` FROM `users` LIMIT %s OFFSET %s"
        cursor.execute(q, (limit, offset))
        users = cursor.fetchall()

        # Query to get the total number of users
        count_query = "SELECT COUNT(*) FROM `users`"
        cursor.execute(count_query)
        result = cursor.fetchone()  # Get the count from the first column

        # Extract the count value
        total_users = result['COUNT(*)'] if result else 0  # Access 'COUNT(*)' key in the dictionary

        for user1 in users:
            user1['user_deleted_at'] = convert_epoch_to_datetime(user1['user_deleted_at'])
            user1['user_blocked_at'] = convert_epoch_to_datetime(user1['user_blocked_at'])
            user1['user_verified_at'] = convert_epoch_to_datetime(user1['user_verified_at'])

        # Render template with paginated content and items
        return render_template("view_admin.html", users=users, page_id=page_id, total_users=total_users, user = user)
    except Exception as ex:
        ic(f"Exception: {ex}")  # Log the error
        if isinstance(ex, x.mysql.connector.Error):
            return "Database error occurred.", 500
        return "System under maintenance.", 500
    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()



# Function to convert epoch to datetime string
def convert_epoch_to_datetime(epoch_time):
    if epoch_time and epoch_time != 0:
        return datetime.utcfromtimestamp(epoch_time).strftime('%Y-%m-%d %H:%M:%S')
    return None  # Return None if the value is 0 or invalid

##############################

@app.get("/admin/block/<user_pk>")
def block_user(user_pk):
    try:
        if not session.get("user", ""):
            return redirect(url_for("view_login"))
        user = session.get("user")
        if not "admin" in user.get("roles", ""):
            return redirect(url_for("view_login"))
        ic("hello")

        user = {
            "user_pk": user_pk,
        }





        btn_unblock = render_template("___btn_unblock_user.html", user=user)

        response = f"""
        <template 
            mix-target="#block-{user['user_pk']}"
            mix-replace>
            {btn_unblock}
        </template>
        """
        return response

    except Exception as ex:
        print(f"Error: {ex}")
        return "Error occurred", 500


    
    finally:
        pass




##############################

@app.post("/admin/user-list/block")
def block_or_unblock_user():
    try:
        if not session.get("user", ""):
            return redirect(url_for("view_login"))
        user = session.get("user")
        if not "admin" in user.get("roles", ""):
            return redirect(url_for("view_login"))
        
        # Get user_pk, action, and page_id from the form
        user_pk = request.form.get("user_pk")
        action = request.form.get("action")
        page_id = request.form.get('page_id', type=int)  # Now it should correctly get the page_id from the form


        if not user_pk or action not in ["block", "unblock"]:
            return redirect(url_for("view_admin"))
        
        db, cursor = x.db()
        
        if action == "block":
            epoch_time = int(time.time())
            query = "UPDATE `users` SET `user_blocked_at` = %s WHERE `user_pk` = %s"
            cursor.execute(query, (epoch_time, user_pk))
        elif action == "unblock":
            query = "UPDATE `users` SET `user_blocked_at` = 0 WHERE `user_pk` = %s"
            cursor.execute(query, (user_pk,))
        
        db.commit()

        # Redirect back to the same page after block/unblock action is performed
        return redirect(url_for("admin_or_pagination", page_id=page_id))

    except Exception as ex:
        if isinstance(ex, x.mysql.connector.Error):
            return f"Database error occurred: {str(ex)}", 500
        return f"An error occurred: {str(ex)}", 500
    
    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()
        
        
        
        
        
        
##############################

@app.get("/item/block/<item_pk>")
def block_item(item_pk):
    try:
        # Define the item (validate if needed)
        item = {
            "item_pk": item_pk  # Add validation logic if required
        }

        # Prepare the Unblock button using a template
        btn_unblock = render_template("___btn_unblock_item.html", item=item)

        epoch_time = int(time.time())
        ic(epoch_time)

        db, cursor = x.db()  # Assuming x.db() returns a database connection and cursor
        q_select = "UPDATE `items` SET `item_blocked_at`= %s WHERE `item_pk`= %s"

        # Execute the query with item_pk as a parameter
        cursor.execute(q_select, (epoch_time, item_pk))

        db.commit()


        # Prepare the response
        response = f"""
        <template 
            mix-target="#block-{item['item_pk']}"
            mix-replace>
            {btn_unblock}
        </template>
        """
        return response

    except Exception as ex:
        print(f"Error: {ex}")
        return "Error occurred", 500



@app.get("/item/unblock/<item_pk>")
def unblock_item(item_pk):
    try:
        # Validate and unblock the item
        item = {
            "item_pk": item_pk
        }


        # Prepare the replacement button (Block)
        btn_block = render_template(
            "___btn_block_item.html", item=item)



        db, cursor = x.db()
        q = "UPDATE `items` SET `item_blocked_at`= 0 WHERE `item_pk` = %s"
        cursor.execute(q, (item_pk,))
        db.commit()



        # Respond with a mix-replace template
        response = f"""
        <template 
            mix-target="#unblock-{item['item_pk']}"
            mix-replace>
            {btn_block}
        </template>
        """
        return response



    except Exception as ex:
        print(f"Error: {ex}")
        return "Error occurred", 500
    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()




##############################

@app.get("/admin/item/list")
def show_admin_item_list():
        try:
            if not session.get("user", ""):
                return redirect(url_for("view_login"))
            user = session.get("user")
            if "admin" not in user.get("roles", ""):
                return redirect(url_for("view_login"))
            
            items = showItemList(1)
            
            # Render template with paginated content and items
            return render_template("view_admin.html", items=items, user=user)
        finally:
            pass





def showItemList(page_id):
    try:
        limit = 20
        offset = (page_id - 1) * limit
        db, cursor = x.db()
        q = "SELECT `item_pk`, `item_title`, `item_price`, `item_image`, `item_blocked_at` FROM `items` LIMIT %s OFFSET %s"
        cursor.execute(q, (limit, offset))
        items = cursor.fetchall()

        return items
    except Exception as ex:
        print(f"Error fetching items: {ex}")
        return []  # Return empty list in case of error
    finally:
        if "cursor" in locals():
            cursor.close()
        if "db" in locals():
            db.close()




#         limit = 20
#         offset = (page_id - 1) * limit  # Offset is based on the page_id
#         db, cursor = x.db()

#         q = "SELECT `item_pk`, `item_title`, `item_price`, `item_image`, `item_blocked_at` FROM `items` LIMIT %s OFFSET %s"
#         cursor.execute(q, (limit, offset))
#         items = cursor.fetchall()



#         # Query to get the total number of users
#         count_query = "SELECT COUNT(*) FROM `items`"
#         cursor.execute(count_query)
#         result = cursor.fetchone()  # Get the count from the first column

#         # Extract the count value
#         total_items = result['COUNT(*)'] if result else 0  # Access 'COUNT(*)' key in the dictionary
#         ic(items)
#         ic(total_items)

#         # Render template with paginated content and items
#         return render_template("view_admin.html", items=items, total_items=total_items)
#     except Exception as ex:
#         ic(f"Exception: {ex}")  # Log the error
#         if isinstance(ex, x.mysql.connector.Error):
#             return "Database error occurred.", 500
#         return "System under maintenance.", 500
#     finally:
#         if "cursor" in locals(): cursor.close()
#         if "db" in locals(): db.close()
    
    
##############################

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
                user_verification_key
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        '''
        cursor.execute(q, (
            user_pk, user_name, user_last_name, user_email, 
            hashed_password, user_created_at, user_deleted_at, user_blocked_at, 
            user_updated_at, user_avatar, user_verified_at, 
            user_verification_key
        ))

        q_add_role = """
            INSERT INTO users_roles (user_role_user_fk, user_role_role_fk) 
            VALUES (%s, %s)
        """
        cursor.execute(q_add_role, (user_pk, user_selected_role))
        
        x.send_verify_email(to_email=user_email, 
                            user_verification_key=user_verification_key)
        db.commit()
    
        return """<template mix-redirect="/login"></template>""", 201
    
    except Exception as ex:
        ic(ex)
        if "db" in locals(): db.rollback()
        if isinstance(ex, x.CustomException): 
            toast = render_template("___toast.html", message=ex.message)
            print ("test1")
            return f"""<template mix-target="#toast" mix-bottom>{toast}</template>""", ex.code    
        if isinstance(ex, x.mysql.connector.Error):
            print ("test2")
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
            ON user_pk = user_role_user_fk
            JOIN roles
            ON role_pk = user_role_role_fk
            WHERE user_email = %s AND user_deleted_at = 0 AND user_verified_at != 0
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

############################## delete item
@app.delete("/items/<item_pk>")
def delete_item(item_pk):
    try:
        # Validate session and permissions
        if not session.get("user", ""): 
            return redirect(url_for("view_login"))

        if not "restaurant" in session.get("user").get("roles"): 
            return redirect(url_for("view_login"))
        
        ic("item_pk: " + item_pk)

        item_pk = x.validate_uuid4(item_pk)

        db, cursor = x.db()

        # Perform the deletion
        q = "DELETE FROM items WHERE item_pk = %s"
        cursor.execute(q, (item_pk,))

        if cursor.rowcount != 1: 
            x.raise_custom_exception("Cannot delete item", 400)

        db.commit()

        # Return template to update the UI
        return f"""
        <template mix-target="#item_{item_pk}" mix-replace></template>
        """

    except Exception as ex:
        if "db" in locals(): db.rollback()
        if isinstance(ex, x.CustomException): 
            return f"""
            <template mix-target="#message" mix-top>{ex.message}</template>
            """, ex.code
        if isinstance(ex, x.mysql.connector.Error):
            return """
            <template mix-target="#message" mix-top>Database error</template>
            """, 500
        return """
        <template mix-target="#message" mix-top>System under maintenance</template>
        """, 500

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
        q = """ UPDATE users
                SET user_verified_at = %s
                WHERE user_verification_key = %s"""
        cursor.execute(q, (user_verified_at, verification_key))
        if cursor.rowcount != 1: x.raise_custom_exception("cannot verify account", 400)
        db.commit()
        return redirect(url_for("view_login", message="User verified, please login"))
 
    except Exception as ex:
        ic(ex)
        if "db" in locals(): db.rollback()
        if isinstance(ex, x.CustomException): return ex.message, ex.code    
        if isinstance(ex, x.mysql.connector.Error):
            ic(ex)
            return "Database under maintenance", 500        
        return "System under maintenance", 500  
    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()


####################
@app.get("/edit_profile")
@x.no_cache
def view_edit_profile():
    if not session.get("user"): 
        return redirect(url_for("view_login"))
    user = session.get("user")
    return render_template("edit_profile.html", user=user, x=x)

@app.post("/edit_profile")
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
@app.get("/delete_profile")
@x.no_cache
def view_delete_profile():
    if not session.get("user"):
        return redirect(url_for("view_login"))
    user = session.get("user")
    ic("Rendering delete_profile.html")
    return render_template("delete_profile.html", user=user)  # 'x' is injected via context processor


######################
@app.post("/request_delete_profile")
@x.no_cache
def request_delete_profile():
    try:
        ic(f"####################################")
        user = session.get("user")
        user_pk = user.get("user_pk")
        user_email = user.get("user_email")
        # printer user pk i terminalen
        ic(f"User PK: {user_pk}")
        ic("Request to delete profile received.")
        if not session.get("user"):
            ic("User not logged in. Redirecting to login.")
            # Optionally, flash a message here if desired
            flash("Please log in to delete your profile.", "warning")
            return redirect(url_for("view_login"))
        


        # Verify password
        user_password = request.form.get("user_password")
        ic(user_password)
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


@app.route("/change_password/<verification_key>", methods=["GET", "POST"])
@x.no_cache
def change_password(verification_key):
    if request.method == "GET":
        return render_template("view_change_password.html", verification_key=verification_key)

    # POST: Update password
    try:
        ic("Updating password with verification key:", verification_key)
        verification_key = x.validate_uuid4(verification_key)
        user_password = x.validate_user_password()
        hashed_password = generate_password_hash(user_password)
        
        db, cursor = x.db()
        try:
            q = """UPDATE users
                   SET user_password = %s
                   WHERE user_verification_key = %s"""
            cursor.execute(q, (hashed_password, verification_key))
            if cursor.rowcount != 1:
                x.raise_custom_exception("Cannot update password", 400)
            db.commit()
        finally:
            cursor.close()
            db.close()

        flash("Password updated successfully. Please log in.", "success")
        return redirect(url_for("view_login"))

    except Exception as ex:
        ic(f"Error during password update: {ex}")
        if isinstance(ex, x.CustomException):
            return render_template("view_change_password.html", error=ex.message, verification_key=verification_key)
        if isinstance(ex, x.mysql.connector.Error):
            return "Database under maintenance", 500
      
      
@app.post("/request_forgot_password")
@x.no_cache
def request_forgot_password():
    try:
        ic("Request to change password received.")
        
        # Verify email
        user_email = x.validate_user_email()

        db, cursor = x.db()
        q = "SELECT user_verification_key FROM users WHERE user_email = %s AND user_deleted_at = 0"

        cursor.execute(q, (user_email,))
        result = cursor.fetchone()  # Fetch one result
        if result:
            user_verification_key = result['user_verification_key']  # Assuming `fetchone()` returns a dictionary
        else:
            x.raise_custom_exception("Email does not exist", 400)

        # Send change password email
        x.send_forgot_password_email(to_email=user_email, user_verification_key=user_verification_key)
        ic("Informational email about changing password sent.")

        # Return a redirect template to trigger frontend redirection
        return f"""<template mix-redirect="{url_for("view_login")}"></template>"""

    except Exception as ex:
        ic(f"Exception occurred during password change request: {ex}")
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
