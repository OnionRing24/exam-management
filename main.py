from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:cset155@localhost/class_exam'
db = SQLAlchemy(app)


class Accounts(db.Model):
    __name__ = 'accounts'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), nullable=False, unique=True)
    role = db.Column(db.String(50), nullable=False)

class Tests(db.Model):
    __name__ = 'tests'
    test_id = db.Column(db.Integer, primary_key=True)
    creator_id = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=False)
    title = db.Column(db.Text, nullable=False)

class Questions(db.Model):
    __name__ = 'questions'
    question_id = db.Column(db.Integer, primary_key=True)
    test_id = db.Column(db.Integer, db.ForeignKey('tests.id'), nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    sort_oder = db.Column(db.Integer, nullable=False, default=0)

@app.before_request
def create_tables():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        new_username = request.form.get('username')
        new_role = request.form.get('role')
        new_row = Accounts(role=new_role, username=new_username)
        
        try:
            db.session.add(new_row)
            db.session.commit()
            return redirect('/')
        except Exception as e:
            db.session.rollback()
            return f"Error: {e}"
    return render_template('register.html')


@app.route('/accounts/')
@app.route('/accounts/<page>')
def get_accounts(page=1):
    page = int(page)
    per_page = 10

    paginated = db.session.query(Accounts).paginate(page=page, per_page=per_page, error_out=False)
    accounts = paginated.items
    
    print(accounts)
    return render_template('accounts.html', accounts=accounts, page=page, per_page=per_page)


if __name__ == '__main__':
    app.run(debug=True)