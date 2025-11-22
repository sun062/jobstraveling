import streamlit as st
import streamlit.components.v1 as components
import os
from datetime import date, datetime 

# --- 1. 환경 설정 및 세션 상태 초기화 ---
st.set_page_config(layout="centered", initial_sidebar_state="expanded")

# 페이지 정의 상수
PAGE_LOGIN = 'login'
PAGE_SIGNUP = 'signup'
PAGE_HOME = 'home'

# 세션 상태 초기화
if 'current_page' not in st.session_state:
    st.session_state.current_page = PAGE_LOGIN
if 'user_data' not in st.session_state:
    st.session_state.user_data = None # 로그인한 사용자 정보
if 'is_auth_ready' not in st.session_state:
    st.session_state.is_auth_ready = False # Firebase 초기화 상태 (현재는 우회)

# --- 2. HTML 파일 로드 함수 (경로 오류 수정 완료) ---
def read_html_file(file_name):
    """HTML 파일을 읽어 문자열로 반환합니다. (htmls 폴더 내에서 파일을 찾습니다)"""
    # 현재 실행 파일(app.py)의 디렉토리를 기준으로 'htmls' 폴더 내의 파일을 찾습니다.
    file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'htmls', file_name)
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        # 오류 메시지에 정확한 파일 경로를 표시하여 디버깅을 돕습니다.
        st.error(f"HTML 파일을 찾을 수 없습니다. 경로를 확인해주세요: {file_path}")
        return ""

# --- 3. 페이지 전환 및 이벤트 처리 ---
def navigate(page):
    """세션 상태를 변경하여 페이지를 전환합니다."""
    st.session_state.current_page = page
    st.rerun()

def handle_component_event(component_value):
    """HTML 컴포넌트에서 받은 이벤트를 처리합니다."""
    if component_value and isinstance(component_value, dict):
        event_type = component_value.get('type')
        payload = component_value.get('payload', {})

        if event_type == 'NAVIGATE_TO':
            target_page = payload.get('page')
            if target_page in [PAGE_LOGIN, PAGE_SIGNUP, PAGE_HOME]:
                navigate(target_page)
        
        elif event_type == 'LOGIN_SUCCESS':
            st.session_state.user_data = payload.get('userData')
            navigate(PAGE_HOME)

        elif event_type == 'SIGNUP_SUCCESS':
            st.session_state.user_data = None 
            navigate(PAGE_LOGIN)

# --- 4. 페이지 렌더링 함수 ---

def render_login_page():
    """로그인 페이지를 렌더링합니다."""
    st.title("로그인")
    
    # HTML 파일을 읽어 컴포넌트로 렌더링
    html_content = read_html_file('login.html')
    if html_content:
        component_value = components.html(
            html_content,
            height=500,
            scrolling=True,
        )
        if component_value is not None:
            handle_component_event(component_value)
    else:
        st.info("HTML 파일을 로드하지 못했습니다. 위의 에러 메시지를 확인해주세요.")
    
    # 로그인 화면일 때만 사이드바에 회원가입 버튼 표시
    st.sidebar.header("새 계정 만들기")
    if st.sidebar.button("회원가입"):
        navigate(PAGE_SIGNUP)

def render_signup_page():
    """회원가입 페이지를 Streamlit 네이티브 폼으로 렌더링합니다. (UI, 유효성 검사 적용)"""
    st.title("회원가입")

    # 오늘 날짜
    today = date.today()
    # 최소 생년월일 (2007년 1월 1일)
    min_date = date(2007, 1, 1)
    
    # 기본 생년월일 설정
    default_birth_date = min_date

    with st.form("signup_form"):
        st.write("사용자 정보를 입력해주세요.")
        
        # 이메일 레이블 수정 완료
        email = st.text_input("이메일 (ID)", key="signup_email")
        password = st.text_input("비밀번호 (6자 이상)", type="password", key="signup_password")
        st.markdown("---")
        school_name = st.text_input("학교 이름", key="signup_school")
        class_number = st.text_input("반 번호", key="signup_class")
        student_name = st.text_input("이름", key="signup_name")
        
        # 생년월일 유효성 검사 적용 (2007년 1월 1일 ~ 오늘 날짜)
        birth_date = st.date_input(
            "생년월일", 
            value=default_birth_date, # 기본값
            min_value=min_date,      # 최소값 (2007년 1월 1일)
            max_value=today,         # 최대값 (오늘 날짜)
            key="signup_birth",
            format="YYYY.MM.DD"
        )
        
        submitted = st.form_submit_button("회원가입 완료")

        if submitted:
            # 유효성 검사
            if not all([email, password, school_name, class_number, student_name, birth_date]):
                st.error("모든 필드를 입력해 주세요.")
            elif len(password) < 6:
                st.error("비밀번호는 6자 이상이어야 합니다.")
            elif birth_date < min_date or birth_date > today:
                 st.error("생년월일은 2007년 1월 1일부터 오늘 날짜까지만 선택 가능합니다.")
            else:
                # **********************************************
                # 현재는 Firebase 통신 오류를 우회하기 위한 가상 성공 처리 로직입니다.
                # 실제 데이터 저장은 이루어지지 않으며 페이지 전환만 진행됩니다.
                # **********************************************
                st.success(f"{student_name}님, 회원가입이 완료되었습니다! 로그인해 주세요.")
                
                # 가상의 사용자 데이터 저장
                fake_user_data = {
                    'email': email,
                    'schoolName': school_name,
                    'classNumber': class_number,
                    'studentName': student_name,
                    'birthDate': birth_date.strftime("%Y-%m-%d")
                }
                st.session_state.temp_signup_data = fake_user_data
                
                # 페이지 전환
                navigate(PAGE_LOGIN)

    st.markdown("---")
    if st.button("로그인 화면으로 돌아가기", key="back_to_login_btn"):
        navigate(PAGE_LOGIN)

def render_home_page():
    """홈 화면을 렌더링합니다."""
    st.title("잡스트레블링 (Job-Trekking) 메인 화면 💼")
    
    user_name = "사용자"
    if st.session_state.user_data and st.session_state.user_data.get('studentName'):
        user_name = st.session_state.user_data['studentName']
        
    st.header(f"환영합니다, {user_name}님!")
    st.write("여기는 로그인 성공 후 보이는 메인 페이지입니다. 사용자 맞춤형 정보와 채용 공고를 탐색할 수 있습니다.")

    if st.button("로그아웃"):
        st.session_state.user_data = None
        navigate(PAGE_LOGIN)

# --- 5. 메인 렌더링 루프 ---

current_user_authenticated = (st.session_state.user_data is not None)

if st.session_state.current_page == PAGE_LOGIN:
    render_login_page()
elif st.session_state.current_page == PAGE_SIGNUP:
    render_signup_page()
elif st.session_state.current_page == PAGE_HOME and current_user_authenticated:
    render_home_page()
else:
    # 예외 상황 처리: 인증되지 않았는데 HOME 페이지이거나, 알 수 없는 페이지인 경우
    st.session_state.current_page = PAGE_LOGIN
    navigate(PAGE_LOGIN)

st.sidebar.markdown(f"**현재 로드 중인 페이지:** {st.session_state.current_page.upper()}")
