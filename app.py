from flask import Flask, request, redirect, url_for, render_template_string
import sqlite3

app = Flask(__name__)

DB = 'stayplus.db'

def init_db():
    with sqlite3.connect(DB) as con:
        con.execute('''
            CREATE TABLE IF NOT EXISTS bookings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                room TEXT,
                checkin TEXT,
                checkout TEXT,
                status TEXT DEFAULT 'รอเช็คอิน'
            )
        ''')

@app.route('/')
def index():
    return '''
    <h1>StayPlus Booking</h1>
    <a href="/admin">เข้าสู่ระบบหลังบ้าน</a>
    <hr>
    <form action="/book" method="post">
        ชื่อผู้จอง: <input name="name" required><br>
        ห้อง: <input name="room" required><br>
        วันที่เช็คอิน: <input type="date" name="checkin" required><br>
        วันที่เช็คเอาต์: <input type="date" name="checkout" required><br>
        <button type="submit">จอง</button>
    </form>
    '''

@app.route('/book', methods=['POST'])
def book():
    name = request.form['name']
    room = request.form['room']
    checkin = request.form['checkin']
    checkout = request.form['checkout']
    with sqlite3.connect(DB) as con:
        con.execute("INSERT INTO bookings (name, room, checkin, checkout) VALUES (?, ?, ?, ?)",
                    (name, room, checkin, checkout))
    return '<p>จองสำเร็จ! <a href="/">กลับหน้าแรก</a> | <a href="/admin">เข้าสู่หลังบ้าน</a></p>'

@app.route('/admin')
def admin():
    with sqlite3.connect(DB) as con:
        bookings = con.execute("SELECT * FROM bookings").fetchall()

    html = '''
    <!DOCTYPE html>
    <html lang="th">
    <head>
        <meta charset="UTF-8">
        <title>หลังบ้าน StayPlus</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-gray-100 p-6">
        <h1 class="text-3xl mb-4 font-bold">ระบบหลังบ้าน StayPlus</h1>
        <a href="/" class="text-blue-600 hover:underline mb-4 inline-block">กลับหน้าแรก</a>
        <table class="table-auto w-full bg-white shadow rounded">
            <thead class="bg-blue-600 text-white">
                <tr>
                    <th class="px-4 py-2">ID</th>
                    <th class="px-4 py-2">ชื่อผู้จอง</th>
                    <th class="px-4 py-2">ห้อง</th>
                    <th class="px-4 py-2">เช็คอิน</th>
                    <th class="px-4 py-2">เช็คเอาต์</th>
                    <th class="px-4 py-2">สถานะ</th>
                    <th class="px-4 py-2">จัดการ</th>
                </tr>
            </thead>
            <tbody>
    '''
    for b in bookings:
        id_, name, room, checkin, checkout, status = b
        status_color = "green" if status == "เช็คอินแล้ว" else "yellow"
        html += f'''
            <tr class="border-b">
                <td class="border px-4 py-2">{id_}</td>
                <td class="border px-4 py-2">{name}</td>
                <td class="border px-4 py-2">{room}</td>
                <td class="border px-4 py-2">{checkin}</td>
                <td class="border px-4 py-2">{checkout}</td>
                <td class="border px-4 py-2 text-{status_color}-600 font-semibold">{status}</td>
                <td class="border px-4 py-2 space-x-2">
                    <form style="display:inline" action="/checkin/{id_}" method="post">
                        <button class="bg-green-500 hover:bg-green-700 text-white px-2 py-1 rounded" type="submit">เช็คอิน</button>
                    </form>
                    <form style="display:inline" action="/delete/{id_}" method="post" onsubmit="return confirm('ลบรายการนี้จริงหรือ?');">
                        <button class="bg-red-500 hover:bg-red-700 text-white px-2 py-1 rounded" type="submit">ลบ</button>
                    </form>
                </td>
            </tr>
        '''
    html += '''
            </tbody>
        </table>
    </body>
    </html>
    '''
    return html

@app.route('/checkin/<int:id_>', methods=['POST'])
def do_checkin(id_):
    with sqlite3.connect(DB) as con:
        con.execute("UPDATE bookings SET status='เช็คอินแล้ว' WHERE id=?", (id_,))
    return redirect(url_for('admin'))

@app.route('/delete/<int:id_>', methods=['POST'])
def delete_booking(id_):
    with sqlite3.connect(DB) as con:
        con.execute("DELETE FROM bookings WHERE id=?", (id_,))
    return redirect(url_for('admin'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
