import threading
import random
import time
from datetime import datetime

# ===================== STORAGE =====================
products = {}
carts = {}
orders = {}
logs = []
order_counter = 1

# ===================== MODELS =====================
class Product:
    def __init__(self, pid, name, price, stock):
        self.pid = pid
        self.name = name
        self.price = price
        self.stock = stock
        self.lock = threading.Lock()

class Order:
    def __init__(self, oid, user_id, items, total):
        self.oid = oid
        self.user_id = user_id
        self.items = items.copy()
        self.total = total
        self.status = "CREATED"
        self.timestamp = datetime.now()

# ===================== LOGGER =====================
def log(msg):
    logs.append(f"{datetime.now()} - {msg}")

# ===================== PRODUCT SERVICE =====================
def add_product():
    pid = input("Product ID: ")
    if pid in products:
        print("❌ Duplicate ID")
        return
    name = input("Name: ")
    price = float(input("Price: "))
    stock = int(input("Stock: "))
    if stock < 0:
        print("❌ Invalid stock")
        return

    products[pid] = Product(pid, name, price, stock)
    log(f"Product {pid} added")

def view_products():
    for p in products.values():
        print(p.pid, p.name, p.price, p.stock)

# ===================== LOCK / STOCK =====================
def reserve_stock(pid, qty):
    product = products.get(pid)
    if not product:
        return False

    with product.lock:
        if product.stock >= qty:
            product.stock -= qty
            return True
        return False

def release_stock(pid, qty):
    products[pid].stock += qty

# ===================== CART SERVICE =====================
def get_cart(user):
    return carts.setdefault(user, {})

def add_to_cart(user):
    pid = input("Product ID: ")
    qty = int(input("Quantity: "))

    if reserve_stock(pid, qty):
        cart = get_cart(user)
        cart[pid] = cart.get(pid, 0) + qty
        log(f"{user} added {pid} qty={qty}")
    else:
        print("❌ Not enough stock")

def remove_from_cart(user):
    cart = get_cart(user)
    pid = input("Product ID: ")

    if pid in cart:
        qty = cart.pop(pid)
        release_stock(pid, qty)
        log(f"{user} removed {pid}")

def view_cart(user):
    cart = get_cart(user)
    for pid, qty in cart.items():
        print(pid, qty)

# ===================== PAYMENT =====================
def process_payment():
    return random.choice([True, False])

# ===================== DISCOUNT =====================
def apply_discount(total, cart):
    for pid, qty in cart.items():
        if qty > 3:
            total *= 0.95

    if total > 1000:
        total *= 0.9

    return total

# ===================== ORDER SERVICE =====================
def place_order(user):
    global order_counter

    cart = get_cart(user)
    if not cart:
        print("❌ Cart empty")
        return

    try:
        total = 0
        for pid, qty in cart.items():
            total += products[pid].price * qty

        total = apply_discount(total, cart)

        oid = f"O{order_counter}"
        order_counter += 1

        order = Order(oid, user, cart, total)
        order.status = "PENDING_PAYMENT"

        # Payment
        if not process_payment():
            raise Exception("Payment Failed")

        order.status = "PAID"
        orders[oid] = order

        carts[user] = {}
        log(f"Order {oid} placed")

        print("✅ Order placed:", oid)

    except Exception as e:
        print("❌ Order failed:", e)
        rollback(cart)

# ===================== ROLLBACK =====================
def rollback(cart):
    for pid, qty in cart.items():
        release_stock(pid, qty)

# ===================== VIEW ORDERS =====================
def view_orders():
    for o in orders.values():
        print(o.oid, o.user_id, o.total, o.status)

# ===================== CANCEL ORDER =====================
def cancel_order():
    oid = input("Order ID: ")
    order = orders.get(oid)

    if not order:
        print("❌ Not found")
        return

    if order.status == "CANCELLED":
        print("Already cancelled")
        return

    order.status = "CANCELLED"

    for pid, qty in order.items.items():
        release_stock(pid, qty)

    log(f"Order {oid} cancelled")
    print("✅ Cancelled")

# ===================== LOW STOCK =====================
def low_stock():
    for p in products.values():
        if p.stock < 5:
            print("⚠ Low:", p.pid, p.stock)

# ===================== RETURN =====================
def return_product():
    oid = input("Order ID: ")
    pid = input("Product ID: ")
    qty = int(input("Qty: "))

    order = orders.get(oid)
    if not order:
        return

    if pid in order.items:
        order.items[pid] -= qty
        release_stock(pid, qty)
        log(f"Return {pid} qty={qty}")

# ===================== CONCURRENCY =====================
def simulate():
    user1 = "A"
    user2 = "B"

    def u1():
        add_to_cart(user1)

    def u2():
        add_to_cart(user2)

    t1 = threading.Thread(target=u1)
    t2 = threading.Thread(target=u2)

    t1.start()
    t2.start()

    t1.join()
    t2.join()

# ===================== LOG VIEW =====================
def view_logs():
    for l in logs:
        print(l)

# ===================== MENU =====================
def menu():
    user = "USER1"

    while True:
        print("\n1.Add Product\n2.View Products\n3.Add to Cart\n4.Remove from Cart")
        print("5.View Cart\n6.Place Order\n7.View Orders\n8.Cancel Order")
        print("9.Low Stock\n10.Return\n11.Concurrent Test\n12.Logs\n0.Exit")

        ch = input("Choice: ")

        if ch == "1":
            add_product()
        elif ch == "2":
            view_products()
        elif ch == "3":
            add_to_cart(user)
        elif ch == "4":
            remove_from_cart(user)
        elif ch == "5":
            view_cart(user)
        elif ch == "6":
            place_order(user)
        elif ch == "7":
            view_orders()
        elif ch == "8":
            cancel_order()
        elif ch == "9":
            low_stock()
        elif ch == "10":
            return_product()
        elif ch == "11":
            simulate()
        elif ch == "12":
            view_logs()
        elif ch == "0":
            break

# ===================== RUN =====================
menu()
