import x
import uuid
import time
import random
from werkzeug.security import generate_password_hash
from faker import Faker
 
fake = Faker()
 
from icecream import ic
ic.configureOutput(prefix=f'***** | ', includeContext=True)
 
 
db, cursor = x.db()
 
 
def insert_user(user):       
    q = f"""
        INSERT INTO users
        VALUES (%s, %s ,%s ,%s ,%s ,%s ,%s ,%s ,%s ,%s ,%s ,%s)        
        """
    values = tuple(user.values())
    cursor.execute(q, values)
 
 
 
 
 
try:
 
 
    
    ##############################
    cursor.execute("DROP TABLE IF EXISTS items") # dependent table
    cursor.execute("DROP TABLE IF EXISTS users_roles") # dependent table
    cursor.execute("DROP TABLE IF EXISTS users")
  
    
    q = """
        CREATE TABLE users (
            user_pk CHAR(36),
            user_name VARCHAR(20) NOT NULL,
            user_last_name VARCHAR(20) NOT NULL,
            user_email VARCHAR(100) NOT NULL UNIQUE,
            user_password VARCHAR(255) NOT NULL,
            user_avatar VARCHAR(50),
            user_created_at INTEGER UNSIGNED,
            user_deleted_at INTEGER UNSIGNED,
            user_blocked_at INTEGER UNSIGNED,
            user_updated_at INTEGER UNSIGNED,
            user_verified_at INTEGER UNSIGNED,
            user_verification_key CHAR(36),
            PRIMARY KEY(user_pk)
        )
        """        
    cursor.execute(q)
 
 
    ##############################
    
    q = """
        CREATE TABLE items (
            item_pk CHAR(36),
            item_user_fk CHAR(36),
            item_title VARCHAR(50) NOT NULL,
            item_price DECIMAL(5,2) NOT NULL,
            item_image VARCHAR(50),
            item_blocked_at INTEGER UNSIGNED,
            PRIMARY KEY(item_pk)
        );
        """
    cursor.execute(q)
    cursor.execute("ALTER TABLE items ADD FOREIGN KEY (item_user_fk) REFERENCES users(user_pk) ON DELETE CASCADE ON UPDATE RESTRICT")
 
 
    ##############################
    cursor.execute("DROP TABLE IF EXISTS roles")
    q = """
        CREATE TABLE roles (
            role_pk CHAR(36),
            role_name VARCHAR(10) NOT NULL UNIQUE,
            PRIMARY KEY(role_pk)
        );
        """        
    cursor.execute(q)
 
 
    ##############################    
    q = """
        CREATE TABLE users_roles (
            user_role_user_fk CHAR(36),
            user_role_role_fk CHAR(36),
            PRIMARY KEY(user_role_user_fk, user_role_role_fk)
        );
        """        
    cursor.execute(q)
    cursor.execute("ALTER TABLE users_roles ADD FOREIGN KEY (user_role_user_fk) REFERENCES users(user_pk) ON DELETE CASCADE ON UPDATE RESTRICT")
    cursor.execute("ALTER TABLE users_roles ADD FOREIGN KEY (user_role_role_fk) REFERENCES roles(role_pk) ON DELETE CASCADE ON UPDATE RESTRICT")
 
 
 
 
 
    ##############################
    # Create roles
    q = f"""
        INSERT INTO roles (role_pk, role_name)
        VALUES ("{x.ADMIN_ROLE_PK}", "admin"), ("{x.CUSTOMER_ROLE_PK}", "customer"),
        ("{x.PARTNER_ROLE_PK}", "partner"), ("{x.RESTAURANT_ROLE_PK}", "restaurant")
        """
    cursor.execute(q)
 
    ##############################
    # Create admin user
    user_pk = str(uuid.uuid4())
    user = {
        "user_pk" : user_pk,
        "user_name" : "Santiago",
        "user_last_name" : "Donoso",
        "user_email" : "admin@fulldemo.com",
        "user_password" : generate_password_hash("password"),
        "user_avatar" : "profile_10.jpg",
        "user_created_at" : int(time.time()),
        "user_deleted_at" : 0,
        "user_blocked_at" : 0,
        "user_updated_at" : 0,
        "user_verified_at" : int(time.time()),
        "user_verification_key" : str(uuid.uuid4())
    }            
    insert_user(user)
    # Assign role to admin user
    q = f"""
        INSERT INTO users_roles (user_role_user_fk, user_role_role_fk) VALUES ("{user_pk}",
        "{x.ADMIN_ROLE_PK}")        
        """    
    cursor.execute(q)    
 
    ##############################
    # Create customer
    user_pk = "4218788d-03b7-4812-bd7d-31c8859e92d8"
    user = {
        "user_pk" : user_pk,
        "user_name" : "John",
        "user_last_name" : "Customer",
        "user_email" : "customer@fulldemo.com",
        "user_password" : generate_password_hash("password"),
        "user_avatar" : "profile_11.jpg",
        "user_created_at" : int(time.time()),
        "user_deleted_at" : 0,
        "user_blocked_at" : 0,
        "user_updated_at" : 0,
        "user_verified_at" : int(time.time()),
        "user_verification_key" : str(uuid.uuid4())
    }
    insert_user(user)
   
    # Assign role to customer user
    q = f"""
        INSERT INTO users_roles (user_role_user_fk, user_role_role_fk) VALUES ("{user_pk}",
        "{x.CUSTOMER_ROLE_PK}")        
        """    
    cursor.execute(q)
 
 
    ##############################
    # Create partner
    user_pk = str(uuid.uuid4())
    user = {
        "user_pk" : user_pk,
        "user_name" : "John",
        "user_last_name" : "Partner",
        "user_email" : "partner@fulldemo.com",
        "user_password" : generate_password_hash("password"),
        "user_avatar" : "profile_12.jpg",
        "user_created_at" : int(time.time()),
        "user_deleted_at" : 0,
        "user_blocked_at" : 0,
        "user_updated_at" : 0,
        "user_verified_at" : int(time.time()),
        "user_verification_key" : str(uuid.uuid4())
    }
    insert_user(user)
    # Assign role to partner user
    q = f"""
        INSERT INTO users_roles (user_role_user_fk, user_role_role_fk) VALUES ("{user_pk}",
        "{x.PARTNER_ROLE_PK}")        
        """    
    cursor.execute(q)
 
    ##############################
    # Create restaurant
    user_pk = str(uuid.uuid4())
    user = {
        "user_pk" : user_pk,
        "user_name" : "John",
        "user_last_name" : "Restaurant",
        "user_email" : "restaurant@fulldemo.com",
        "user_password" : generate_password_hash("password"),
        "user_avatar" : "profile_13.jpg",
        "user_created_at" : int(time.time()),
        "user_deleted_at" : 0,
        "user_blocked_at" : 0,
        "user_updated_at" : 0,
        "user_verified_at" : int(time.time()),
        "user_verification_key" : str(uuid.uuid4())
    }
    insert_user(user)
    
    # Assign role to restaurant user
    q = f"""
        INSERT INTO users_roles (user_role_user_fk, user_role_role_fk) VALUES ("{user_pk}",
        "{x.RESTAURANT_ROLE_PK}")        
        """    
    cursor.execute(q)
 
 
    ##############################
    # Create 50 customer
 
    domains = ["example.com", "testsite.org", "mydomain.net", "website.co", "fakemail.io", "gmail.com", "hotmail.com"]
    user_password = hashed_password = generate_password_hash("password")
    for _ in range(50):
        user_pk = str(uuid.uuid4())
        user_verified_at = random.choice([0,int(time.time())])
        user = {
            "user_pk" : user_pk,
            "user_name" : fake.first_name(),
            "user_last_name" : fake.last_name(),
            "user_email" : fake.unique.user_name() + "@" + random.choice(domains),
            "user_password" : user_password,
            # user_password = hashed_password = generate_password_hash(fake.password(length=20))
            "user_avatar" : "profile_"+ str(random.randint(1, 100)) +".jpg",
            "user_created_at" : int(time.time()),
            "user_deleted_at" : 0,
            "user_blocked_at" : 0,
            "user_updated_at" : 0,
            "user_verified_at" : user_verified_at,
            "user_verification_key" : str(uuid.uuid4())
        }
 
        insert_user(user)
        cursor.execute("""INSERT INTO users_roles (
            user_role_user_fk,
            user_role_role_fk)
            VALUES (%s, %s)""", (user_pk, x.CUSTOMER_ROLE_PK))
 
 
    ##############################
    # Create 50 partners
 
    user_password = hashed_password = generate_password_hash("password")
    for _ in range(50):
        user_pk = str(uuid.uuid4())
        user_verified_at = random.choice([0,int(time.time())])
        user = {
            "user_pk" : user_pk,
            "user_name" : fake.first_name(),
            "user_last_name" : fake.last_name(),
            "user_email" : fake.unique.email(),
            "user_password" : user_password,
            "user_avatar" : "profile_"+ str(random.randint(1, 100)) +".jpg",
            "user_created_at" : int(time.time()),
            "user_deleted_at" : 0,
            "user_blocked_at" : 0,
            "user_updated_at" : 0,
            "user_verified_at" : user_verified_at,
            "user_verification_key" : str(uuid.uuid4())
        }
 
        insert_user(user)
 
        cursor.execute("""
        INSERT INTO users_roles (
            user_role_user_fk,
            user_role_role_fk)
            VALUES (%s, %s)
        """, (user_pk, x.PARTNER_ROLE_PK))
 
    ##############################
    # Create 50 restaurants
    dishes = ["Spaghetti Carbonara","Chicken Alfredo","Beef Wellington","Sushi","Pizza Margherita","Tacos","Caesar Salad","Fish and Chips","Pad Thai","Dim Sum","Croissant","Ramen","Lasagna","Burrito","Chicken Parmesan","Tom Yum Soup","Shawarma","Paella","Hamburger","Pho","Chicken Tikka Masala","Moussaka","Goulash","Bangers and Mash","Peking Duck","Falafel","Ceviche","Chili Con Carne","Ratatouille","Beef Stroganoff","Fajitas","Samosas","Lobster Roll","Arancini","Tiramisu","Beef Empanadas","Poutine","Biryani","Hummus","Schnitzel","Meatloaf","Quiche","Paella Valenciana","Clam Chowder","Sweet and Sour Pork","Enchiladas","Crepes","Masala Dosa","Gnocchi","Jambalaya","Pork Ribs","Tandoori Chicken","Nasi Goreng","Kimchi","Roti","Lamb Tagine","Risotto","Croque Monsieur","Beef Burritos","Baked Ziti","Yakitori","Fettuccine Alfredo","Peking Duck Pancakes","Empanadas","Ahi Poke","Cacciatore","Pappardelle","Cannelloni","Empanadas de Pollo","Gado-Gado","Carne Asada","Chicken Katsu","Falafel Wrap","Maki Rolls","Stuffed Bell Peppers","Souvlaki","Bibimbap","Tofu Stir Fry","Chilaquiles","Mango Sticky Rice","Ragu","Beef Brisket","Tortilla Española","Panzanella","Chicken Shawarma","Pesto Pasta","Bulgogi","Maki Sushi","Cordon Bleu","Blini with Caviar","Clafoutis","Salmon Teriyaki","Shrimp Scampi","Frittata","Chateaubriand","Crab Cakes","Chicken Fried Rice","Hot Pot","Mole Poblano","Tofu Scramble"]
 
    # Predefined lists for generating restaurant names
    prefixes = ['Golden', 'Blue', 'Silver', 'Royal', 'Epic', 'Happy', 'Urban', 'Cozy', 'Mellow', 'Mystic']
    suffixes = ['Grill', 'Café', 'Bistro', 'Bar', 'Restaurant', 'Lounge', 'Diner', 'Steakhouse', 'Tavern', 'Pizzeria']
    types_of_cuisine = ['Italian', 'Mexican', 'Indian', 'Chinese', 'French', 'Japanese', 'Mediterranean', 'American', 'Vietnamese', 'Thai']
 
    # Generate a fake restaurant name
    def generate_restaurant_name():
        prefix = prefixes[fake.random_int(0, len(prefixes) - 1)]
        suffix = suffixes[fake.random_int(0, len(suffixes) - 1)]
        cuisine = types_of_cuisine[fake.random_int(0, len(types_of_cuisine) - 1)]
        
        return f"{prefix} {fake.word().capitalize()} {suffix} - {cuisine}"
 
    user_password = hashed_password = generate_password_hash("password")
    for _ in range(50):
        user_pk = str(uuid.uuid4())
        user_verified_at = random.choice([0,int(time.time())])
        user = {
            "user_pk" : user_pk,
            "user_name" : generate_restaurant_name()[:20],  # Generate fake restaurant name for user_name
            "user_last_name" : "",
            "user_email" : fake.unique.email(),
            "user_password" : user_password,
            "user_avatar" : "profile_"+ str(random.randint(1, 100)) +".jpg",
            "user_created_at" : int(time.time()),
            "user_deleted_at" : 0,
            "user_blocked_at" : 0,
            "user_updated_at" : 0,
            "user_verified_at" : user_verified_at,
            "user_verification_key" : str(uuid.uuid4())
        }
        insert_user(user)
 
        cursor.execute("""
        INSERT INTO users_roles (
            user_role_user_fk,
            user_role_role_fk)
            VALUES (%s, %s)
        """, (user_pk, x.RESTAURANT_ROLE_PK))
 
        for _ in range(random.randint(5,50)):
            dish_id = random.randint(1, 100)
            cursor.execute("""
            INSERT INTO items (
                item_pk, item_user_fk, item_title, item_price, item_image, item_blocked_at)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (str(uuid.uuid4()), user_pk, random.choice(dishes), round(random.uniform(50, 999), 2), f"dish_{dish_id}.jpg", 0))
 
 
 
 
    db.commit()
 
except Exception as ex:
    ic(ex)
    if "db" in locals(): db.rollback()
 
finally:
    if "cursor" in locals(): cursor.close()
    if "db" in locals(): db.close()