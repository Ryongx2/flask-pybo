from datetime import datetime

from flask import Blueprint, render_template, request, url_for, g, flash
from werkzeug.utils import redirect

from .. import db
from ..models import Question, Answer, User
from ..forms import QuestionForm, AnswerForm
# from pybo.models import Question
# from pybo.forms import QuestionForm

# 3-08 모델 수정하기 @login_required 적용하기
from pybo.views.auth_views import login_required

bp = Blueprint('question', __name__, url_prefix='/question')

# 3-14 검색 함수 (_list() 수정)
@bp.route('/list/')
def _list():
    page = request.args.get('page', type=int, default=1)
    kw = request.args.get('kw', type=str, default='')
    question_list = Question.query.order_by(Question.create_date.desc())
    if kw:
        search = '%%{}%%'.format(kw)
        sub_query = db.session.query(Answer.question_id, Answer.content, User.username) \
            .join(User, Answer.user_id == User.id).subquery()
        question_list = question_list \
            .join(User) \
            .outerjoin(sub_query, sub_query.c.question_id == Question.id) \
            .filter(Question.subject.ilike(search) |  # 질문제목
                    Question.content.ilike(search) |  # 질문내용
                    User.username.ilike(search) |  # 질문작성자
                    sub_query.c.content.ilike(search) |  # 답변내용
                    sub_query.c.username.ilike(search)  # 답변작성자
                    ) \
            .distinct()
    question_list = question_list.paginate(page=page, per_page=10)
    return render_template('question/question_list.html', question_list=question_list, page=page, kw=kw)

# @bp.route('/list/')
# def _list():
#     # 페이지 적용
#     page = request.args.get('page', type=int, default=1) # 페이지
#     # GET 방식으로 요청한 URL에서 page값을 가져올 때 사용.
#     # list는 파이썬의 예약어이기 때문에 함수명을 _list로 지정.
#     question_list = Question.query.order_by(Question.create_date.desc())
#     question_list = question_list.paginate(page=page, per_page=10)
#     # paginate 함수의 첫번 째 인수로 전달된 page : 현재 조회할 페이지의 번호, 두번 째 인수 per_page : 페이지마다 보여 줄 게시물이 10건임.
#     return render_template('question/question_list.html', question_list=question_list)

@bp.route('/detail/<int:question_id>/')
def detail(question_id):
    form = AnswerForm()
    question = Question.query.get_or_404(question_id)
    return render_template('question/question_detail.html', question=question, form=form)
# 질문 상세 템플릿에 폼이 추가되었으므로 question_views.py 파일의 detail 함수도 폼을 사용하도록 수정해야 함.
# 이 과정이 없으면 템플릿에서 form 객체를 읽지 못해 오류 발생.

@bp.route('/create/', methods=('GET', 'POST'))
# 3-08 모델 수정하기 @login_required 적용하기
@login_required
def create():
    form = QuestionForm()
    if request.method == 'POST' and form.validate_on_submit():
        # form.validate_in_submit 함수 : 전송된 폼 데이터의 정합성을 점검.
        #   즉, QuestionForm 클래스의 각 속성에 지정한 DataRequired() 같은 점검 항목에 이상이 없는지 확인함.
        # -> POST 요청, 폼 데이터에 이상이 없을 경우 질문을 저장한 뒤 main.index 페이지로 이동하라.
        question = Question(subject=form.subject.data, content=form.content.data,
                            create_date=datetime.now(), user=g.user)
        db.session.add(question)
        db.session.commit()
        return redirect(url_for('main.index'))
    return render_template('question/question_form.html', form=form)
# question_form.html 템플릿에 전달하는 QuestionForm의 객체(form)는 템플릿에서 라벨이나 입력폼 등을 만들때 필요함.

# 3-10 질문 수정 라우팅 함수
@bp.route('/modify/<int:question_id>', methods=('GET', 'POST'))
@login_required
def modify(question_id):
    question = Question.query.get_or_404(question_id)
    if g.user != question.user:
        flash('수정권한이 없습니다')
        # 만약 로그인한 사용자와 질문의 작성자가 다르면 수정할 수 없도록 flash 오류 발생.
        # flash 함수는 강제로 오류를 발생시키는 함수로, 로직에 오류가 있을 경우 사용한다.
        return redirect(url_for('question.detail', question_id=question_id))
    if request.method == 'POST':  # POST 요청
        form = QuestionForm()
        if form.validate_on_submit():
            form.populate_obj(question)
            question.modify_date = datetime.now()  # 수정일시 저장
            db.session.commit()
            return redirect(url_for('question.detail', question_id=question_id))
    else:  # GET 요청
        form = QuestionForm(obj=question)
    return render_template('question/question_form.html', form=form)

# 3-10 질문 삭제 라우팅 함수
@bp.route('/delete/<int:question_id>')
@login_required
def delete(question_id):
    question = Question.query.get_or_404(question_id)
    if g.user != question.user:
        flash('삭제권한이 없습니다.')
        return redirect(url_for('question.detail', question_id=question_id))
    db.session.delete(question)
    db.session.commit()
    return redirect(url_for('question._list'))

# 3-11 질문 추천 라우팅 함수
@bp.route('/vote/<int:question_id>/')
@login_required
def vote(question_id):
    _question = Question.query.get_or_404(question_id)
    if g.user == _question.user:
        flash('본인이 작성한 글은 추천할 수 없습니다.')
    else:
        _question.voter.append(g.user)
        # Question 모델의 voter는 여러 사람이 추가할 수 있는 다대다 관계이므로 _question.voter.append(g.user)와 같이 append 함수로 추천인을 추가해야 한다.
        # question_voter 테이블의 구조상 같은 사용자가 같은 질문을 여러 번 추천해도 추천 횟수는 증가하지 않는다.
        # 동일한 사용자를 append 할 때 오류가 날 것 같지만 내부적으로 중복되지 않도록 잘 처리된다.
        db.session.commit()
    return redirect(url_for('question.detail', question_id=question_id))