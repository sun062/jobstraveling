import streamlit as st
import streamlit.components.v1 as components
import os
from datetime import date, timedelta, datetime # datetime 모듈 추가

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

# --- 2. HTML 파일 로드 함수 ---
def read_html_file(file_name):
    """HTML 파일을 읽어 문자열로 반환합니다."""
    # 파일 경로를 os.path.join을 사용하여 안전하게 조합
    file_path = os.path.join(os.path.dirname(__file__), 'htmls', file_name)
    try:
        # 현재 환경에서는 'htmls' 폴더 없이 현재 디렉토리에 있다고 가정
        # 실제 환경에 맞게 경로를 조정해주세요.
        if os.path.exists(file_name):
             with open(file_name, 'r', encoding='utf-8') as f:
                return f.read()
        else:
            # 기본 경로에서 파일을 찾지 못하면 오류 메시지 반환
            return ""
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
            # 회원가입 성공 시 로그인 화면으로 전환
            st.session_state.user_data = None 
            navigate(PAGE_LOGIN)

# --- 4. 페이지 렌더링 함수 ---

def render_html(html_file_name, height=600):
    """HTML 컴포넌트를 렌더링하고, 반환 값을 이벤트 핸들러로 전달합니다."""
    # 이 환경에서는 htmls/login.html 파일을 직접 읽을 수 없으므로, 
    # Streamlit은 현재 파일을 로드하는 기능을 지원하지 않아 임시로 파일 내용을 직접 넣을 수 없습니다.
    # GitHub에 업로드하실 때는 login.html 파일도 함께 업로드하셔야 합니다.
    
    # 임시 HTML 콘텐츠 (실제 코드가 아닙니다. GitHub에 올리실 때는 'login.html'을 별도 파일로 올리셔야 합니다.)
    if html_file_name == 'login.html':
         html_content = """
         <div style="text-align: center; padding: 20px; border: 1px solid #ccc; border-radius: 8px;">
             <h3>로그인 페이지 (HTML 파일 별도 확인 필요)</h3>
             <p>실제 로직은 login.html 파일에 있습니다.</p>
             <button onclick="window.parent.postMessage({'type': 'NAVIGATE_TO', 'payload': {'page': 'signup'}}, '*')">회원가입 페이지로</button>
         </div>
         """
    else:
        return

    component_value = components.html(
        html_content,
        height=height,
        scrolling=True,
    )

    # HTML 컴포넌트에서 값이 반환되면 이벤트 처리 함수 호출
    if component_value is not None:
        handle_component_event(component_value)

def render_login_page():
    """로그인 페이지를 렌더링합니다."""
    st.title("로그인")
    
    # HTML 파일을 직접 읽어 컴포넌트로 렌더링 (이전 로직 복원)
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
        st.info("HTML 파일을 찾을 수 없습니다. GitHub에 'htmls/login.html' 파일을 확인해주세요.")
    
    # 로그인 화면일 때만 사이드바에 회원가입 버튼 표시
    st.sidebar.header("새 계정 만들기")
    if st.sidebar.button("회원가입"):
        navigate(PAGE_SIGNUP)

def render_signup_page():
    """회원가입 페이지를 Streamlit 네이티브 폼으로 렌더링합니다. (UI 및 유효성 검사 반영)"""
    st.title("회원가입")

    # 오늘 날짜
    today = date.today()
    # 최소 생년월일 (2007년 1월 1일)
    min_date = date(2007, 1, 1)
    
    # 기본 생년월일 설정 (예: 2007년생이 현재 고등학생이라면 2007년 1월 1일로 설정)
    default_birth_date = min_date

    with st.form("signup_form"):
        st.write("사용자 정보를 입력해주세요.")
        
        # 1. 이메일 레이블 수정 ("아이디" -> "이메일")
        email = st.text_input("이메일 (ID)", key="signup_email")
        password = st.text_input("비밀번호 (6자 이상)", type="password", key="signup_password")
        st.markdown("---")
        school_name = st.text_input("학교 이름", key="signup_school")
        class_number = st.text_input("반 번호", key="signup_class")
        student_name = st.text_input("이름", key="signup_name")
        
        # 2. 생년월일 유효성 검사 적용 (2007년 1월 1일 ~ 오늘 날짜)
        birth_date = st.date_input(
            "생년월일", 
            value=default_birth_date, # 기본값
            min_value=min_date,      # 최소값 (2007년 1월 1일)
            max_value=today,         # 최대값 (오늘 날짜)
            key="signup_birth",
            format="YYYY.MM.DD"
        )
        
        # 버튼
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
                # 실제 Firebase 저장 로직은 이 환경에서 실행 불가하므로,
                # 시연을 위해 성공적으로 처리된 것으로 간주하고 페이지 전환
                # **********************************************
                st.success(f"{student_name}님, 회원가입이 완료되었습니다! 로그인해 주세요.")
                
                # 가상의 사용자 데이터 (실제 저장되는 데이터 형태를 가정)
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
                st.session_state.current_page = PAGE_LOGIN # navigate 호출 후 session state를 직접 변경하는 것은 안전하지 않으나, 여기서는 시연을 위해 유지

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
