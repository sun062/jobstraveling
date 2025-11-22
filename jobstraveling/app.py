import streamlit as st
import streamlit.components.v1 as components
import os

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
    st.session_state.user_data = None # 로그인한 사용자 정보 (초기화 오류 해결)
if 'is_auth_ready' not in st.session_state:
    st.session_state.is_auth_ready = False # Firebase 초기화 상태 (현재는 우회)

# --- 2. HTML 파일 로드 함수 ---
def read_html_file(file_name):
    """HTML 파일을 읽어 문자열로 반환합니다."""
    # 파일 경로를 os.path.join을 사용하여 안전하게 조합
    file_path = os.path.join(os.path.dirname(__file__), 'htmls', file_name)
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        st.error(f"HTML 파일을 찾을 수 없습니다: {file_name}")
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
            # HTML 컴포넌트에서 받은 페이지 전환 요청 처리
            target_page = payload.get('page')
            if target_page in [PAGE_LOGIN, PAGE_SIGNUP, PAGE_HOME]:
                navigate(target_page)
        
        elif event_type == 'LOGIN_SUCCESS':
            # 로그인 성공 시 사용자 데이터 저장 및 홈 화면으로 전환
            st.session_state.user_data = payload.get('userData')
            navigate(PAGE_HOME)

        elif event_type == 'SIGNUP_SUCCESS':
            # 회원가입 성공 시 로그인 화면으로 전환 (현재는 네이티브 폼에서 처리)
            st.session_state.user_data = None # 사용자 데이터 초기화
            navigate(PAGE_LOGIN)

# --- 4. 페이지 렌더링 함수 ---

def render_html(html_file_name, current_page_key, height=600):
    """HTML 컴포넌트를 렌더링하고, 반환 값을 이벤트 핸들러로 전달합니다."""
    html_content = read_html_file(html_file_name)
    if not html_content:
        return

    # st.components.v1.html() 호출 시 'key' 인수는 제거합니다. (버전 호환성 문제 해결)
    component_value = components.html(
        html_content,
        height=height,
        scrolling=True,
        # key=current_page_key, # 문제가 되는 key 인수는 제거되었습니다.
    )

    # HTML 컴포넌트에서 값이 반환되면 이벤트 처리 함수 호출
    if component_value is not None:
        handle_component_event(component_value)

def render_login_page():
    """로그인 페이지를 렌더링합니다."""
    st.title("로그인")
    render_html('login.html', 'login_page_key', height=500)
    
    # 로그인 화면일 때만 사이드바에 회원가입 버튼 표시
    st.sidebar.header("새 계정 만들기")
    if st.sidebar.button("회원가입"):
        navigate(PAGE_SIGNUP)

def render_signup_page():
    """회원가입 페이지를 Streamlit 네이티브 폼으로 렌더링합니다. (통신 문제 우회)"""
    st.title("회원가입")
    
    with st.form("signup_form"):
        st.write("사용자 정보를 입력해주세요.")
        
        # 입력 필드
        email = st.text_input("이메일 (ID)", key="signup_email")
        password = st.text_input("비밀번호 (6자 이상)", type="password", key="signup_password")
        st.markdown("---")
        school_name = st.text_input("학교 이름", key="signup_school")
        class_number = st.text_input("반 번호", key="signup_class")
        student_name = st.text_input("이름", key="signup_name")
        birth_date = st.date_input("생년월일", key="signup_birth")
        
        # 버튼
        submitted = st.form_submit_button("회원가입 완료")

        if submitted:
            # 유효성 검사 (간단화)
            if not all([email, password, school_name, class_number, student_name, birth_date]):
                st.error("모든 필드를 입력해 주세요.")
            elif len(password) < 6:
                st.error("비밀번호는 6자 이상이어야 합니다.")
            else:
                # **********************************************
                # 실제 Firebase 저장 로직은 이 환경에서 실행 불가하므로,
                # 시연을 위해 성공적으로 처리된 것으로 간주하고 페이지 전환
                # **********************************************
                st.success(f"{student_name}님, 회원가입이 완료되었습니다! 로그인해 주세요.")
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

# --- 6. 기타 설정 (임시로 사용되지 않음) ---
# 이 부분은 현재 회원가입 로직이 Python 네이티브 폼으로 대체되면서 사용되지 않습니다.
# 필요한 경우 나중에 주석을 풀고 사용합니다.
# current_page_key = f"{st.session_state.current_page}_key"
