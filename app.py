from flask import Flask, render_template, request, redirect, url_for, jsonify
import sqlite3

app = Flask(__name__)

# Koneksi ke database
def connect_db():
    return sqlite3.connect('database.db')

# Membuat tabel jika belum ada
def create_table():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS orders (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        nama TEXT,
                        menu TEXT,
                        harga REAL,
                        jumlah INTEGER,
                        total REAL,
                        status TEXT DEFAULT "Menunggu")''')
    conn.commit()
    conn.close()

create_table()

# Halaman utama pelanggan
@app.route('/')
def home_page():
    return render_template('home.html')

# Halaman pembayaran pelanggan
@app.route('/pembayaran', methods=['GET', 'POST'])
def pembayaran():
    if request.method == 'POST':
        data = request.json
        nama = data['nama']
        menu = data['menu']
        harga = float(data['harga'].replace("$", ""))
        jumlah = int(data['jumlah'])
        total = harga * jumlah

        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO orders (nama, menu, harga, jumlah, total, status) VALUES (?, ?, ?, ?, ?, ?)",
                       (nama, menu, harga, jumlah, total, "Menunggu"))
        conn.commit()
        conn.close()

        return jsonify({"success": True, "message": "Pesanan berhasil disimpan!"})

    return render_template('pembayaran.html')

# Halaman status pesanan pelanggan
@app.route('/status/<nama>')
def status_pesanan(nama):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT menu, jumlah, total, status FROM orders WHERE nama = ?", (nama,))
    orders = cursor.fetchall()
    conn.close()

    return render_template('status.html', nama=nama, orders=orders)

# Halaman admin untuk melihat semua pesanan
@app.route('/admin')
def admin():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM orders")
    orders = cursor.fetchall()
    conn.close()

    return render_template('admin.html', orders=orders)

# API untuk memperbarui status pesanan oleh admin
@app.route('/update_status', methods=['POST'])
def update_status():
    data = request.json
    order_id = data['id']
    new_status = data['status']

    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE orders SET status = ? WHERE id = ?", (new_status, order_id))
    conn.commit()
    conn.close()

    return jsonify({"success": True, "message": "Status berhasil diperbarui"})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')