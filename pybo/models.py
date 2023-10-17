from pybo import db
# db객체는 __init__.py 파일에서 생성한 SQLAlchemy 클래스의 객체.

# 3-11 question_voter 테이블 객체 작성
question_voter = db.Table(
    'question_voter',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), primary_key=True),
    db.Column('question_id', db.Integer, db.ForeignKey('question.id', ondelete='CASCADE'), primary_key=True)
)

# 3-11 Answer 모델에 voter 속성 추가하기 - 테이블 객체 answer_voter를 생성한 후 Answer 모델에 voter 속성을 추가하여 연결함.
answer_voter = db.Table(
    'answer_voter',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), primary_key=True),
    db.Column('answer_id', db.Integer, db.ForeignKey('answer.id', ondelete='CASCADE'), primary_key=True)
)

# 질문 모델 생성하기
# Question과 같은 모델 클래스는 db.Model 클래스를 상속하여 만들어야 함.
class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text(), nullable=False)
    create_date = db.Column(db.DateTime(), nullable=False)

    # 3-08 Question 모델에 글쓴이 추가 (user_id, user)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    # user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=True, server_default='1')
    # user_id : User 모델을 Question 모델과 연결하기 위한 속성 / server_default에서 지정한 '1'은 최초로 생성한 User 모델 데이터의 id 값을 의미함.
    user = db.relationship('User', backref=db.backref('question_set'))
    # user : Question 모델에서 User 모델을 참조하기 위한 속성

    # 3-10 게시물 수정&삭제 - modify_date 속성 추가
    modify_date = db.Column(db.DateTime(), nullable=True)

    # 3-11 Question 모델에 voter 속성 추가하기
    voter = db.relationship('User', secondary=question_voter, backref=db.backref('question_voter_set'))
    # voter의 backref 이름은 question_voter_set으로 지정해 주었다.
    #   만약 어떤 계정이 a_user라는 객체로 참조되었다면 a_user.question_voter_set으로 해당 계정이 추천한 질문 리스트를 구할 수 있다.

# 답변 모델 생성하기
class Answer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id', ondelete='CASCADE'))
    # 외래키 : 'question 테이블의 id 컬럼', 삭제 연동 설정 : CASCADE - 질문 삭제 시 해당 질문에 달린 답변도 삭제
    question = db.relationship('Question', backref=db.backref('answer_set'))
    # 파이썬 코드를 이용하여 질문 데이터 삭제 시 연관된 답변 데이터를 모두 삭제하는 방법
    # question = db.relationship('Question', backref=db.backref('answer_set', cascade='all, delete-orphan'))
    content = db.Column(db.Text(), nullable=False)
    create_date = db.Column(db.DateTime(), nullable=False)

    # Answer 모델에 글쓴이 추가(user_id, user)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    # user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=True, server_default='1')
    user = db.relationship('User', backref=db.backref('answer_set'))

    # 3-10 게시물 수정&삭제 - modify_date 속성 추가
    modify_date = db.Column(db.DateTime(), nullable=True)

    # 3-11 Answer 모델에 voter 속성 추가하기
    voter = db.relationship('User', secondary=answer_voter, backref=db.backref('answer_voter_set'))


# 회원 모델 생성하기 - 속성 : username, password, email
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    # unique=True : 같은 값을 저장할 수 없다. -> username과 email이 중복되어 저장되지 않는다.