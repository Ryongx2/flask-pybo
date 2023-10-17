from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, PasswordField, EmailField
from wtforms.validators import DataRequired, Length, EqualTo, Email

# 질문을 등록할 때 사용할 QuestionForm (플라스크 폼) - QuestionForm과 같은 플라스크의 폼은 FlaskForm 클래스를 상속하여 만들어야 함.
class QuestionForm(FlaskForm):
    # QuestionForm의 속성 : "제목"(글자수 제한 O - StringField 사용), "내용"(글자수 제한 X - TextAreaField 사용)
    subject = StringField('제목', validators=[DataRequired('제목은 필수입력 항목입니다.')])
    # 첫번째 입력인수인 "제목"은 폼 라벨(Label)이다. 템플릿에서 이 라벨을 이용하여 "제목"이라는 라벨을 출력할 수 있다.
    # 두번째 입력인수는 validators이다. validators는 검증을 위해 사용하는 도구로 필수 항목인지를 체크하는 DataRequired, 이메일인지를 체크하는 Email,
    #   길이를 체크하는 Length 등이 있다. 예를들어 필수값이면서 이메일이어야 하면 validators=[DataRequired(), Email()] 과 같이 사용할 수 있다.
    content = TextAreaField('내용', validators=[DataRequired('내용은 필수입력 항목입니다.')])

# 답변 등록을 할 때 사용할 AnswerForm (플라스크 폼)
class AnswerForm(FlaskForm):
    content = TextAreaField('내용', validators=[DataRequired('내용은 필수입력 항목입니다.')])

# 회원가입 폼 UserCreateForm (플라스크 폼)
class UserCreateForm(FlaskForm):
    username = StringField('사용자이름', validators=[DataRequired(), Length(min=3, max=25)])
    # username은 필수항목, 길이가 3-25 사이여야 한다는 검증조건 설정. (Length는 폼 유효성 검증시 문자열의 길이가 최소길이(min)와 최대길이(max) 사이에 해당하는지를 검증함.)
    password1 = PasswordField('비밀번호', validators=[
        DataRequired(), EqualTo('password2', '비밀번호가 일치하지 않습니다')])
    # password1 속성에 지정된 EqualTo('password2')는 password1과 password2의 값이 일치해야 함을 의미함.
    # PasswordFrield는 StringField와 비슷하지만 템플릿에서 자동변환으로 사용시 <input type="password"> 태그로 변환됨.
    password2 = PasswordField('비밀번호확인', validators=[DataRequired()])
    # password1 속성과 password2 속성은 모두 필수값, 두개의 값이 일치해야하는 EqualTo 검증이 추가됨.
    email = EmailField('이메일', validators=[DataRequired(), Email()])
    # EmailField 역시 StringField와 동일하지만 템플릿 자동변환으로 사용시 <input type="email"> 태그로 변환됨.
    # email 속성에는 필수값 검증조건에 더하여 Email() 검증조건이 추가됨. Email() 검증조건 : 해당 속서으이 값이 이메일형식과 일치하는지를 검증함.

# 로그인 폼 UserLoginForm (플라스크 폼)
class UserLoginForm(FlaskForm):
    username = StringField('사용자이름', validators=[DataRequired(), Length(min=3, max=25)])
    password = PasswordField('비밀번호', validators=[DataRequired()])






























