from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:cset155@localhost/class_exam'
db = SQLAlchemy(app)


class Accounts(db.Model):
    __name__ = 'accounts'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), nullable=False, unique=True)
    # PW
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
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            return f"Error: {e}"
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        user_exists = Accounts.query.filter_by(username=username).first()
        if user_exists:
            return redirect('/')
        else:
            db.session.rollback()
            return f"Error: {Exception}"
    return render_template('login.html')


@app.route('/accounts/')
@app.route('/accounts/<page>')
def get_accounts(page=1):
    page = int(page)
    per_page = 10

    paginated = db.session.query(Accounts).paginate(page=page, per_page=per_page, error_out=False)
    accounts = paginated.items
    
    print(accounts)
    return render_template('accounts.html', accounts=accounts, page=page, per_page=per_page)


@app.route('/tests/')
@app.route('/tests/<page>')
def get_tests(page=1):
    page = int(page)
    per_page = 10

    paginated = db.session.query(Tests).paginate(page=page, per_page=per_page, error_out=False)
    tests = paginated.items
    
    print(tests)
    return render_template('tests.html', tests=tests, page=page, per_page=per_page)


@app.route('/create_test', methods=['GET', 'POST'])
def create_test():
    if request.method == 'POST':
        new_title = request.form.get('title')
        new_creator = request.form.get('creator')
        new_row = Accounts(title=new_title, creator_id=new_creator)
        
        try:
            db.session.add(new_row)
            db.session.commit()
            return redirect('/')
        except Exception as e:
            db.session.rollback()
            return f"Error: {e}"
    return render_template('create_test.html')


@app.route('/edit_test/<int:test_id>', methods=['GET'])
def update_get_requrest(test_id):
    try:
        test = Tests.query.get(test_id)
    
        if test is None:
            return render_template('edit_test.html', error='Test not found!', test=None)
        return render_template('edit_test.html', test=test)
    
    except Exception as e:
        db.session.rollback()
        return f"Error: {e}"

if __name__ == '__main__':
    app.run(debug=True)