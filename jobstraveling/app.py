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
    # 모의 로그인 데이터를 저장하는 세션 상태 추가 (기본값 설정)
    st.session_state.mock_user = {
        'email': 'user@example.com',
        'password': 'password123',
        'schoolName': '가상고등학교',
        'classNumber': '301',
        'studentName': '홍길동',
        'birthDate': '2007-01-01'
    } 

# --- 2. HTML 파일 로드 함수 (더 이상 사용하지 않지만 구조 유지를 위해 남겨둠) ---
def read_html_file(file_name):
    """HTML 파일을 읽어 문자열로 반환합니다. (htmls 폴더 내에서 파일을 찾습니다)"""
    file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'htmls', file_name)
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        st.error(f"HTML 파일을 찾을 수 없습니다. 경로를 확인해주세요: {file_path}")
        return ""

# --- 3. 페이지 전환 및 이벤트 처리 ---
def navigate(page):
    """세션 상태를 변경하여 페이지를 전환합니다."""
    st.session_state.current_page = page
    st.rerun()

# HTML 컴포넌트 방식 사용 중단: handle_component_event 함수 삭제

# --- 4. 페이지 렌더링 함수 ---

def render_login_page():
    """
    로그인 페이지를 Streamlit 네이티브 폼으로 렌더링합니다.
    (HTML 컴포넌트의 통신 오류를 해결하기 위해 통합)
    """
    st.title("로그인")
    
    # 중앙 정렬을 위한 컨테이너
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        # 로그인 폼
        with st.form("login_form", clear_on_submit=False):
            st.markdown('<h3 style="text-align: center; color: #3b82f6;">Job-Trekking 로그인</h3>', unsafe_allow_html=True)
            
            # Mock 사용자 정보 미리보기 (디버깅용)
            mock_user = st.session_state.mock_user
            st.info(f"💡 **Mock 계정:**\n- **이메일:** `{mock_user['email']}`\n- **비밀번호:** `{mock_user['password']}`")
            
            email = st.text_input("이메일 주소", key="login_email")
            password = st.text_input("비밀번호", type="password", key="login_password")
            
            login_submitted = st.form_submit_button("로그인")
            
            if login_submitted:
                # 1. 유효성 검사
                if not all([email, password]):
                    st.error("이메일과 비밀번호를 모두 입력해 주세요.")
                    return
                
                # 2. Mock 로그인 처리 (실제 DB 연동은 이 위치에 구현 예정)
                if (st.session_state.mock_user and 
                    st.session_state.mock_user['email'] == email and 
                    st.session_state.mock_user['password'] == password):
                    
                    st.success("모의 로그인 성공! 홈 화면으로 이동합니다.")
                    
                    # Mock 사용자 데이터에서 민감 정보(password) 제거 후 저장
                    user_data = {**st.session_state.mock_user}
                    user_data.pop('password', None)
                    st.session_state.user_data = user_data
                    
                    # 페이지 전환 (st.rerun()을 포함)
                    navigate(PAGE_HOME)
                    
                else:
                    st.error("이메일 또는 비밀번호가 올바르지 않습니다.")

        # 회원가입 버튼 (폼 밖에서 네이티브 버튼으로 처리)
        if st.button("회원가입", key="navigate_to_signup"):
            navigate(PAGE_SIGNUP)


def render_signup_page():
    """회원가입 페이지를 Streamlit 네이티브 폼으로 렌더링합니다."""
    st.title("회원가입")

    # 오늘 날짜와 최소 날짜 설정 (2007년 1월 1일)
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
                # Mock 데이터 저장 및 성공 처리
                # 이 데이터는 이후 로그인 검증에 사용됩니다.
                st.session_state.mock_user = {
                    'email': email,
                    'password': password, # Mock 검증을 위해 임시 저장
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
