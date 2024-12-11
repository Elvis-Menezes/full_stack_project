from flask import Flask, render_template, request, session, redirect, url_for
from datetime import datetime
from flask_mysqldb import MySQL

app = Flask(__name__)

# Configure MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '26673999'
app.config['MYSQL_DB'] = 'database'

mysql = MySQL(app)

@app.route('/')
def root():
    session['logged_out'] = 1
    return render_template('index.html')

@app.route('/index.html')
def index():
    return render_template('index.html')

@app.route('/header_page.html')
def header_page():
    return render_template('header_page.html')

@app.route('/menu-bar-charity.html')
def menu_bar_charity():
    return render_template('menu-bar-charity.html')

@app.route('/footer.html')
def footer():
    return render_template('footer.html')

@app.route('/sidebar.html')
def sidebar():
    return render_template('sidebar.html')

@app.route('/contact.html')
def contact():
    return render_template('contact.html')

@app.route('/our-causes.html')
def our_causes():
    return render_template('our-causes.html')

@app.route('/about-us.html')
def about_us():
    return render_template('about-us.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nm = request.form['nm']
        contact = request.form['contact']
        email = request.form['email']
        password = request.form['password']

        cur = mysql.connection.cursor()
        cur.execute("SELECT Email FROM Users WHERE Email = %s", (email,))
        data = cur.fetchone()
        if data:
            user_exists = 1
        else:
            user_exists = 0
            cur.execute("INSERT INTO Users (Name, Email, Password, Contact) VALUES (%s, %s, %s, %s)",
                        (nm, email, password, contact))
            mysql.connection.commit()
        cur.close()
        return render_template('login.html', user_exists=user_exists, invalid=None, logged_out=None)
    return render_template('register.html')

@app.route('/login.html', methods=['GET', 'POST'])
def login():
    invalid = None
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        cur = mysql.connection.cursor()
        cur.execute("SELECT Name FROM Users WHERE Email = %s AND Password = %s", (email, password))
        user = cur.fetchone()
        if user:
            session['nm'] = user[0]
            session['email'] = email
            session['logged_out'] = None
            return redirect(url_for('donate'))
        else:
            invalid = 1
        cur.close()
    return render_template('login.html', user_exists=None, invalid=invalid, logged_out=None)

@app.route('/logout')
def logout():
    session.clear()
    session['logged_out'] = 1
    return render_template('index.html')

@app.route('/donate')
def donate():
    if session.get('logged_out', 1):
        return render_template('login.html', logged_out=1, user_exists=None, invalid=None)
    return render_template('donate.html', nm=session['nm'], email=session['email'])

@app.route('/donation', methods=['POST'])
def donation():
    if session.get('logged_out', 1):
        return render_template('login.html', logged_out=1, user_exists=None, invalid=None)
    nm = session['nm']
    email = session['email']
    amt = request.form['amt']
    today = datetime.now().strftime("%d-%m-%Y, %H:%M")

    cur = mysql.connection.cursor()
    cur.execute("SELECT Email FROM Donors WHERE Email = %s", (email,))
    if cur.fetchone():
        cur.execute("UPDATE Donors SET Amount = Amount + %s WHERE Email = %s", (amt, email))
    else:
        cur.execute("INSERT INTO Donors (Name, Amount, Email, timestamp) VALUES (%s, %s, %s, %s)",
                    (nm, amt, email, today))
    mysql.connection.commit()

    cur.execute("SELECT Amount FROM Donors WHERE Email = %s", (email,))
    Amount = cur.fetchone()[0]
    cur.close()

    msg = "Thank You for Donating"
    return render_template("greeting.html", msg=msg, nm=nm, Amount=Amount, today=today, email=email)

@app.route('/list1')
def list1():
    if session.get('logged_out', 1):
        return render_template('login.html', logged_out=1, user_exists=None, invalid=None)

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM Donors")
    rows = cur.fetchall()
    cur.close()
    return render_template("list1.html", rows=rows)

@app.route('/profile')
def profile():
    if session.get('logged_out', 1):
        return render_template('login.html', logged_out=1, user_exists=None, invalid=None)

    cur = mysql.connection.cursor()
    cur.execute("SELECT Contact, Password FROM Users WHERE Email = %s", (session['email'],))
    user_details = cur.fetchone()
    cur.close()

    contact, password = user_details
    return render_template("profile.html", nm=session['nm'], email=session['email'], contact=contact, password=password)

if __name__ == '__main__':
    app.secret_key = "your_secret_key"
    app.run()
