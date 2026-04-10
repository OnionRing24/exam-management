from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:cset155@localhost/class_exam'
db = SQLAlchemy(app)
app.secret_key = 'hello'


class Accounts(db.Model):
    __tablename__ = 'accounts'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), nullable=False, unique=True)
    role = db.Column(db.String(50), nullable=False)

class Tests(db.Model):
    __tablename__ = 'tests'
    test_id = db.Column(db.Integer, primary_key=True)
    creator_id = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=False)
    title = db.Column(db.Text, nullable=False)
    questions = db.relationship('Questions', backref='test', cascade='all, delete-orphan')

class Questions(db.Model):
    __tablename__ = 'questions'
    question_id = db.Column(db.Integer, primary_key=True)
    test_id = db.Column(db.Integer, db.ForeignKey('tests.test_id'), nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    responses = db.relationship('Responses', backref='question', cascade='all, delete-orphan')

class Responses(db.Model):
    __tablename__ = 'responses'
    response_id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.question_id'), nullable=False)
    test_id = db.Column(db.Integer, db.ForeignKey('tests.test_id'), nullable=False)
    response_text = db.Column(db.Text, nullable=False)
    grade = db.Column(db.Integer, nullable=True)



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
            print(user_exists)
            session.permanent = True
            session['username'] = username
            session['user_id'] = user_exists.id
            session['role'] = user_exists.role
            print(session['username'])
            return redirect('/')
        else:
            db.session.rollback()
            return f"Error: {Exception}"
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')


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
        new_row = Tests(title=new_title, creator_id=session['user_id'])
        
        try:
            db.session.add(new_row)
            db.session.commit()
            return redirect('/')
        except Exception as e:
            db.session.rollback()
            return f"Error: {e}"
    return render_template('create_test.html')


@app.route('/delete_test/<int:test_id>', methods=['POST'])
def delete_test(test_id):
    test = Tests.query.get(test_id)
    
    if not test:
        return "Test not found", 404
    
    # Verify ownership
    if test.creator_id != session['user_id']:
        return "You can only delete tests you created", 403
    
    db.session.delete(test)
    db.session.commit()
    return redirect('/')


@app.route('/edit_test/<int:test_id>', methods=['GET'])
def update_get_request(test_id):
    try:
        test = Tests.query.filter_by(test_id=test_id).first()

        if test is None:
            return render_template('edit_test.html', error='test not found', test=None, questions=[])
        
        questions = Questions.query.filter_by(test_id=test_id).all()

        return render_template('edit_test.html', test=test, questions=questions, error=None)
    except Exception as e:
        print(e)
        return render_template('edit_test.html', error=str(e), test=None, questions=[])



@app.route('/edit_test/<int:test_id>', methods=['POST'])
def update_test(test_id):
    try:
        test = Tests.query.filter_by(test_id=test_id).first()
        
        if test is None:
            return render_template('edit_test.html', error='test not found', test=None)
        
        test.title = request.form['title']
        db.session.commit()
        
        question_texts = request.form.getlist('question_text')
        for question_text in question_texts:
            if question_text.strip():
                new_question = Questions(test_id=test_id, question_text=question_text)
                db.session.add(new_question)
        
        db.session.commit()
        
        questions = Questions.query.filter_by(test_id=test_id).all()
        return render_template('edit_test.html', error=None, success="Data updated successfully!", test=test, questions=questions)
    except Exception as e:
        db.session.rollback()
        print(e)
        return render_template('edit_test.html', error=str(e), success=None, test=test, questions=[])


@app.route('/take_test/<int:test_id>', methods=['GET'])
def participate_get_request(test_id):
    try:
        test = Tests.query.filter_by(test_id=test_id).first()

        if test is None:
            return render_template('take_test.html', error='test not found', test=None, questions=[])
        
        questions = Questions.query.filter_by(test_id=test_id).all()

        return render_template('take_test.html', test=test, questions=questions, error=None)
    except Exception as e:
        print(e)
        return render_template('take_test.html', error=str(e), test=None, questions=[])


@app.route('/take_test/<int:test_id>', methods=['POST'])
def submit_test(test_id):
    try:
        test = Tests.query.filter_by(test_id=test_id).first()
        
        if test is None:
            return render_template('take_test.html', error='test not found', test=None, questions=[])
        
        # Get all responses from the form
        response_texts = request.form.getlist('response_text')
        question_ids = request.form.getlist('question_id')
        
        # Create a response for each question
        for question_id, response_text in zip(question_ids, response_texts):
            if question_id.strip():
                new_response = Responses(question_id=int(question_id),response_text=response_text, student_id=session['user_id'], test_id=test_id)
                db.session.add(new_response)
        
        db.session.commit()
        return redirect(url_for('index'))  # Or wherever you want to redirect
        
    except Exception as e:
        db.session.rollback()
        print(e)
        questions = Questions.query.filter_by(test_id=test_id).all()
        return render_template('take_test.html', error=str(e), test=test, questions=questions)


@app.route('/responses/<int:test_id>', methods=['GET'])
def view_responses(test_id):
    results = db.session.query(
        Responses.response_id,
        Responses.student_id,
        Questions.question_text, 
        Responses.response_text,
        Responses.grade
    )\
    .join(Questions, Responses.question_id == Questions.question_id)\
    .filter(Responses.test_id == test_id)\
    .distinct()\
    .all()
    
    from collections import defaultdict
    response_by_student = defaultdict(list)
    
    for row in results:
        response_by_student[row[1]].append({
            'response_id': row[0],
            'question_text': row[2],
            'response_text': row[3],
            'grade': row[4]
        })
    
    success = request.args.get('success')
    error = request.args.get('error')
    
    return render_template('responses.html', response=response_by_student, success=success, error=error, test_id=test_id)


@app.route('/responses/<int:test_id>', methods=['POST'])
def grade_responses(test_id):
    try:
        grades = request.form.getlist('response_grade')
        response_ids = request.form.getlist('response_id')
        
        for response_id, grade in zip(response_ids, grades):
            if grade:  # Only update if grade is provided
                response_obj = Responses.query.get(response_id)
                if response_obj:
                    response_obj.grade = int(grade)
        
        db.session.commit()
        return redirect(url_for('view_responses', test_id=test_id, success='Grades saved successfully!'))
    except Exception as e:
        db.session.rollback()
        print(e)
        return redirect(url_for('view_responses', test_id=test_id, error=f'Error saving grades: {str(e)}'))


if __name__ == '__main__':
    app.run(debug=True)