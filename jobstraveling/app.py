import streamlit as st
import streamlit.components.v1 as components
import os
import json 
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
    st.session_state.is_auth_ready = False 
if 'mock_user' not in st.session_state:
    # 기본 Mock 사용자 정보 설정 (회원가입 전 기본 로그인 테스트용)
    st.session_state.mock_user = {
        'email': 'test@example.com',
        'password': 'password123',
        'schoolName': '가상고등학교',
        'classNumber': '301',
        'studentName': '홍길동',
        'birthDate': '2007-01-01'
    } 

# --- 2. HTML 파일 로드 함수 ---
def read_html_file(file_name):
    """HTML 파일을 읽어 문자열로 반환합니다. (htmls 폴더 내에서 파일을 찾습니다)"""
    file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'htmls', file_name)
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        st.error(f"HTML 파일을 찾을 수 없습니다. 경로를 확인해주세요: {file_path}")
        return ""

# --- 3. 페이지 전환 ---
def navigate(page):
    """세션 상태를 변경하여 페이지를 전환합니다."""
    st.session_state.current_page = page
    st.rerun()

# --- 4. 페이지 렌더링 함수 ---

def render_login_page():
    """로그인 페이지를 Streamlit 네이티브 폼으로 렌더링합니다. (안정적인 로그인 방식)"""
    st.title("로그인")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("login_form", clear_on_submit=False):
            st.markdown('<h3 style="text-align: center; color: #3b82f6;">Job-Trekking 로그인</h3>', unsafe_allow_html=True)
            
            st.info("💡 **팁:** 회원가입 시 입력하신 이메일과 비밀번호로 로그인해 주세요.")
            
            email = st.text_input("이메일 주소", key="login_email")
            password = st.text_input("비밀번호", type="password", key="login_password")
            
            login_submitted = st.form_submit_button("로그인")
            
            if login_submitted:
                # 1. 유효성 검사
                if not all([email, password]):
                    st.error("이메일과 비밀번호를 모두 입력해 주세요.")
                    return
                
                # 2. Mock 로그인 처리 (회원가입 시 저장된 mock_user 정보와 대조)
                mock_user = st.session_state.mock_user
                
                if (mock_user and 
                    mock_user.get('email') == email and 
                    mock_user.get('password') == password):
                    
                    st.success("로그인 성공! 홈 화면으로 이동합니다.")
                    
                    # Mock 사용자 데이터에서 민감 정보(password) 제거 후 저장
                    user_data = {**mock_user}
                    user_data.pop('password', None)
                    st.session_state.user_data = user_data
                    
                    # 페이지 전환
                    navigate(PAGE_HOME)
                    
                else:
                    st.error("이메일 또는 비밀번호가 올바르지 않습니다.")

        if st.button("회원가입", key="navigate_to_signup"):
            navigate(PAGE_SIGNUP)


def render_signup_page():
    """회원가입 페이지를 Streamlit 네이티브 폼으로 렌더링합니다."""
    st.title("회원가입")

    today = date.today()
    min_date = date(2007, 1, 1)
    default_birth_date = min_date

    with st.form("signup_form"):
        st.write("사용자 정보를 입력해주세요.")
        
        email = st.text_input("이메일 주소", key="signup_email")
        password = st.text_input("비밀번호 (6자 이상)", type="password", key="signup_password")
        st.markdown("---")
        school_name = st.text_input("학교 이름", key="signup_school")
        class_number = st.text_input("반 번호", key="signup_class")
        student_name = st.text_input("이름", key="signup_name")
        
        birth_date = st.date_input(
            "생년월일", 
            value=default_birth_date,
            min_value=min_date,
            max_value=today,
            key="signup_birth",
            format="YYYY.MM.DD"
        )
        
        submitted = st.form_submit_button("회원가입 완료")

        if submitted:
            # 유효성 검사 및 Mock 데이터 저장 로직은 동일합니다.
            if not all([email, password, school_name, class_number, student_name, birth_date]):
                st.error("모든 필드를 입력해 주세요.")
            elif len(password) < 6:
                st.error("비밀번호는 6자 이상이어야 합니다.")
            elif birth_date < min_date or birth_date > today:
                 st.error("생년월일은 2007년 1월 1일부터 오늘 날짜까지만 선택 가능합니다.")
            else:
                # Mock 데이터 저장 
                st.session_state.mock_user = {
                    'email': email,
                    'password': password, 
                    'schoolName': school_name,
                    'classNumber': class_number,
                    'studentName': student_name,
                    'birthDate': birth_date.strftime("%Y-%m-%d")
                }
                
                st.success(f"{student_name}님, 회원가입이 완료되었습니다! 이제 이 정보로 로그인해 주세요.")
                
                # 페이지 전환
                navigate(PAGE_LOGIN)

    st.markdown("---")
    if st.button("로그인 화면으로 돌아가기", key="back_to_login_btn"):
        navigate(PAGE_LOGIN)

def render_home_page():
    """
    홈 화면을 렌더링합니다. (Tailwind CSS 디자인이 적용된 HTML 컴포넌트를 사용하여 형태 복구)
    """
    user_name = "사용자"
    user_info = st.session_state.user_data
    if user_info and user_info.get('studentName'):
        user_name = user_info['studentName']
        
    # === 요청된 문구 수정 반영: '잡스트레블링 (Job-Trekking) 메인 화면 💼' -> '잡스트레블링 메인 화면 💼'
    st.title("잡스트레블링 메인 화면 💼")
    
    # === 요청된 문구 수정 반영: '홈 화면 (업데이트됨)' -> '홈 화면'
    st.write(f"환영합니다, **{user_name}**님! 아래는 '홈 화면'의 콘텐츠입니다.")
    
    # home.html 파일 읽기
    html_content = read_html_file('home.html')
    
    if html_content:
        # 사용자 이름 등 동적 데이터를 HTML에 주입
        # 이름 외에 학교, 반 정보도 함께 전달
        html_content = html_content.replace('{{USER_NAME}}', user_name)
        html_content = html_content.replace('{{USER_SCHOOL}}', user_info.get('schoolName', '학교 정보 없음'))
        html_content = html_content.replace('{{USER_CLASS}}', user_info.get('classNumber', '반 정보 없음'))
        
        components.html(
            html_content,
            height=700, # 충분한 높이 확보
            scrolling=True,
        )
    
    st.markdown("---")
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
    # 인증되지 않은 상태에서 홈 화면 접근 시 로그인 페이지로 리다이렉션
    st.session_state.current_page = PAGE_LOGIN
    navigate(PAGE_LOGIN)

st.sidebar.markdown(f"**현재 로드 중인 페이지:** {st.session_state.current_page.upper()}")

