from datetime import datetime

from flask import Blueprint, url_for, request, render_template, g, flash
from werkzeug.utils import redirect

from .. import db
from ..forms import AnswerForm
from ..models import Question, Answer
# from pybo import db
# from pybo.models import Question, Answer

# 3-08 모델 수정하기 @login_required 적용하기
from .auth_views import login_required

bp = Blueprint('answer', __name__, url_prefix='/answer')

#답변 등록은 POST요청만 있으므로 GET, POST 분기처리는 필요 없음.
@bp.route('/create/<int:question_id>', methods=('POST',))
# 3-08 모델 수정하기 @login_required 적용하기
@login_required
def create(question_id):
    form = AnswerForm()
    question = Question.query.get_or_404(question_id)
    if form.validate_on_submit():
        content = request.form['content']
        # 템플릿의 form 엘리먼트를 통해 전달된 데이터들은 create 함수에서 request 객체로 얻을 수 있다.
        # request.form['content'] 코드는 POST 폼 방식으로 전송된 데이터 항복 중 name 속성이 content인 값을 의미한다.
        answer = Answer(content=content, create_date=datetime.now(), user=g.user)
        # g.user는 세션에 저장된 사용자 정보 데이터이다. g.user는 auth_view.py 파일의 @bp.before_app_request 애너테이션에 의해 생성된다.
        question.answer_set.append(answer)
        # question.answer_set은 "질문에 달린 답변들"을 의미한다.
        # Question과 Answer 모델이 연결되어 있어 backref에 설정한 answer_set을 사용할 수 있음.
        db.session.commit()
        # return redirect(url_for('question.detail', question_id=question_id))
        # 3-12 앵커로 이동
        return redirect('{}#answer_{}'.format(
            url_for('question.detail', question_id=question_id), answer.id))

    return render_template('question/question_detail.html', question=question, form=form)

# 3-10 답변 수정 라우팅 함수
@bp.route('/modify/<int:answer_id>', methods=('GET', 'POST'))
@login_required
def modify(answer_id):
    answer = Answer.query.get_or_404(answer_id)
    if g.user != answer.user:
        flash('수정권한이 없습니다')
        return redirect(url_for('question.detail', question_id=answer.question.id))
    if request.method == "POST":
        form = AnswerForm()
        if form.validate_on_submit():
            form.populate_obj(answer)
            answer.modify_date = datetime.now()  # 수정일시 저장
            db.session.commit()
            # return redirect(url_for('question.detail', question_id=answer.question.id))
            # 3-12 앵커로 이동
            return redirect('{}#answer_{}'.format(
                url_for('question.detail', question_id=answer.question.id), answer.id))
    else:
        form = AnswerForm(obj=answer)
    return render_template('answer/answer_form.html', form=form)

# 3-10 답변 삭제 라우팅 함수
@bp.route('/delete/<int:answer_id>')
@login_required
def delete(answer_id):
    answer = Answer.query.get_or_404(answer_id)
    question_id = answer.question.id
    if g.user != answer.user:
        flash('삭제권한이 없습니다')
    else:
        db.session.delete(answer)
        db.session.commit()
    return redirect(url_for('question.detail', question_id=question_id))

# 3-11 답변 추천 라우팅 함수
@bp.route('/vote/<int:answer_id>/')
@login_required
def vote(answer_id):
    answer = Answer.query.get_or_404(answer_id)
    if g.user == answer.user:
        flash('본인이 작성한 글은 추천할 수 없습니다')
    else:
        answer.voter.append(g.user)
        db.session.commit()
    # return redirect(url_for('question.detail', question_id=_answer.question.id))
    # 3-12 앵커로 이동
    return redirect('{}#answer_{}'.format(
                url_for('question.detail', question_id=answer.question.id), answer.id))
