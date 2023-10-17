from flask import Blueprint, url_for, render_template, flash, request, session, g
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import redirect

from pybo import db
from pybo.forms import UserCreateForm, UserLoginForm
from pybo.models import User
# 3-08 모델 수정하기 @login_required 데코레이터
import functools

bp = Blueprint('auth', __name__, url_prefix='/auth')
# /auth/로 시작하는 URL이 호출되면 auth_view.py 파일의 함수들이 호출될 수 있도록 블루프린트 객체 bp를 생성함.

# 회원가입을 위한 signup 함수 생성 -> signup 함수는 POST 방식에는 계정을 저장하고, GET 방식에는 계정 등록 화면을 출력함.
@bp.route('/signup/', methods=('GET', 'POST'))
def signup():
    form = UserCreateForm()
    if request.method == 'POST' and form.validate_on_submit():

        user = User.query.filter_by(username=form.username.data).first()
        # username으로 데이터를 조회해서 "이미 등록된 사용자"인지를 확인함.

        if not user:
            user = User(username=form.username.data,
                        password=generate_password_hash(form.password1.data),
                        # 비밀번호는 폼으로 전달받은 값을 그대로 저장하지 않고 generate_password_hash 함수로 암호화하여 저장함.
                        # generate_password_hash 함수로 암호화한 데이터는 복호화할 수 없다. 그래서 로그인할 때 입력받은 비밀번호는 암호화하여 저장된 비밀번호와 비교해야 한다.
                        email=form.email.data)
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('main.index'))
        else:
            flash('이미 존재하는 사용자입니다.')

    return render_template('auth/signup.html', form=form)

# 로그인을 수행할 라우팅 함수
@bp.route('/login/', methods=('GET', 'POST'))
# POST 방식에는 로그인을 수행하고, GET 요청에는 로그인 화면을 보여줌.
def login():
    form = UserLoginForm()
    if request.method == 'POST' and form.validate_on_submit():

        error = None
        user = User.query.filter_by(username=form.username.data).first()
        # 폼 입력으로 받은 username으로 데이터베이스에 해당하는 사용자가 있는지 검사.

        if not user:
            error = "존재하지 않는 사용자입니다."

        elif not check_password_hash(user.password, form.password.data):
            # 데이터베이스에 저장된 비밀번호는 암호화되었으므로 입력된 비밀번호와 바로 비교할 수 없다.
            # 입력 비밀번호는 반드시 check_password_hash 함수로 암호화한 후 데이터베이스의 값과 비교해야 함.
            error = "비밀번호가 올바르지 않습니다."

        if error is None:
            # 사용자도 존재하고 비밀번호도 일치한다면 플라스크 세션(session)에 사용자 정보를 저장함.
            session.clear()
            session['user_id'] = user.id
            # 세션 키에 'user_id'라는 문자열을 저장하고 키에 해당하는 값은 데이터베이스에서 조회한 사용자의 id 값을 저장함.

            # 3-08 모델 수정하기 @login_required 데코레이터
            _next = request.args.get('next', '')
            if _next:
                return redirect(_next)
            else:
                return redirect(url_for('main.index'))
            # return redirect(url_for('main.index'))
            # 로그인 후 메인 화면으로
        flash(error)

    return render_template('auth/login.html', form=form)

#   session은 request와 마찬가지로 플라스크가 자체적으로 생성하여 제공하는 객체이다.
# 브라우저가 플라스크 서버에 요청을 보내면 request 객체는 요청할 때마다 새로운 객체가 생성된다.
# 하지만 session은 request와 달리 한번 생성하면 그 값을 계속 유지하는 특성이 있다.
# session은 서버에 브라우저별로 생성되는 메모리 공간이라고 할 수 있다.
# 따라서 세션에 사용자의 id값을 저장하면 다양한 URL 요청에 이 세션에 저장된 값을 읽을 수 있다.
# 예를 들어 세션 정보를 확인하여 현재 요청한 주체가 로그인한 사용자인지 아닌지 판별할 수 있다.

# 로그인 여부 확인 함수
@bp.before_app_request
# 이 애너테이션이 적용된 함수는 라우팅 함수보다 항상 먼저 실행됨. 즉, 앞으로 load_logged_in_user 함수는 모든 라우팅 함수보다 먼저 실행됨.
# @bp.before_app_request를 적용한 함수는 auth_views.py의 라우팅 함수 뿐만 아니라 모든 라우팅 함수보다 항상 먼저 실행됨.
def load_logged_in_user():
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
        # 여기서 사용한 g는 플라스크의 컨텍스트 변수이다. 이 변수는 request 변수와 마찬가지로 [요청 -> 응답] 과정에서 유효하다.
    else:
        g.user = User.query.get(user_id)
        # session 변수에 user_id 값이 있으면 데이터베이스에서 사용자 정보를 조회하여 g.user에 저장한다.
        # 이렇게 하면 이후 사용자 로그인 검사를 할 떄 session을 조사할 필요가 없다. g.user에 값이 있는지만 확인하면 된다.
        # g.user에는 User 객체가 저장되어 있으므로 여러 가지 사용자 정보(username, email 등)를 추가로 얻어내는 이점이 있다.
        # g.user에는 User 객체가 저장된다.

# 로그아웃 라우팅 함수
@bp.route('/logout/')
def logout():
    session.clear()
    # 세션의 모든 값을 삭제할 수 있도록 session.clear() 추가.
    # -> session에 저장된 user_id는 삭제 될 것이며, load_logged_in_user 함수에서 session의 값을 읽을 수 없으므로 g.user도 None이 됨.
    return redirect(url_for('main.index'))

# 3-08 모델 수정하기 @login_required 데코레이터
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(*args, **kwargs):
        if g.user is None:
            _next = request.url if request.method == 'GET' else ''
            return redirect(url_for('auth.login', next=_next))
        return view(*args, **kwargs)
    return wrapped_view






























