from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:root@cset155/class_exam (your database name)'
db = SQLAlchemy(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET'])
def create_get_request():
    return render_template('register.html')

@app.route('/register', methods=['POST'])
def create_account():
    if request.form.get('password') == request.form.get('confirm_password'):
        if request.form.get('username'):
            pass

if __name__ == '__main__':
    app.run(debug=True)