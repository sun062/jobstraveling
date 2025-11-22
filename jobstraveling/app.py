# jobstraveling/app.py
import streamlit as st
import json
import os
import pathlib
import time

# --- 환경 변수 로드 (더미 값) ---
# __app_id와 __firebase_config는 Canvas 환경에서 자동으로 제공됩니다.
# 이 코드는 Canvas 외부 실행 환경을 위한 더미 값입니다.
# 실제 Canvas 환경에서는 __app_id와 __firebase_config 변수가 사용됩니다.
appId = "default-app-id" 
firebaseConfig = os.environ.get('FIREBASE_CONFIG')

if firebaseConfig:
    try:
        FIREBASE_CONFIG_JSON_STRING = firebaseConfig
    except Exception:
        FIREBASE_CONFIG_JSON_STRING = '{"apiKey": "DUMMY_API_KEY", "authDomain": "DUMMY_AUTH_DOMAIN", "projectId": "DUMMY_PROJECT_ID", "storageBucket": "DUMMY_STORAGE_BUCKET", "messagingSenderId": "DUMMY_MESSAGING_SENDER_ID", "appId": "DUMMY_APP_ID"}'
else:
    # Firebase 설정이 없는 경우를 대비한 안전한 JSON 문자열
    FIREBASE_CONFIG_JSON_STRING = '{"apiKey": "DUMMY_API_KEY", "authDomain": "DUMMY_AUTH_DOMAIN", "projectId": "DUMMY_PROJECT_ID", "storageBucket": "DUMMY_STORAGE_BUCKET", "messagingSenderId": "DUMMY_MESSAGING_SENDER_ID", "appId": "DUMMY_APP_ID"}'

# --- 페이지 파일 정의 ---
# 파일 경로를 정의합니다.
PAGE_LOGIN = 'login'
PAGE_SIGNUP = 'signup'
PAGE_HOME = 'home' # 메인 화면은 아직 구현되지 않았지만, 상태로 정의합니다.

PAGE_FILES = {
    PAGE_LOGIN: 'htmls/login.html',
    PAGE_SIGNUP: 'htmls/signup.html',
    # PAGE_HOME: 'htmls/home.html' # 홈 화면은 아직 구현되지 않았습니다.
}

# --- 파일 읽기 유틸리티 함수 ---
def read_html_file(file_path):
    """HTML 파일을 읽고 내용을 반환합니다."""
    base_path = pathlib.Path(__file__).parent.resolve()
    full_path = base_path / file_path
    
    try:
        with open(full_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        st.error(f"Error: HTML file not found at {full_path}")
        return None
    except Exception as e:
        st.error(f"Error reading file {file_path}: {e}")
        return None

# --- Streamlit 상태 초기화 ---
if 'current_page' not in st.session_state:
    # --- 디버깅을 위한 임시 변경: 새로고침 시 signup에 머물도록 강제 ---
    # 디버깅 완료 후에는 st.session_state.current_page = PAGE_LOGIN 으로 변경해야 합니다.
    st.session_state.current_page = PAGE_SIGNUP # 로그인 대신 회원가입 페이지를 기본값으로 설정
    st.session_state.user_data = None

# --- HTML 컴포넌트 이벤트 처리 함수 ---
def handle_html_event(event_data):
    """HTML 컴포넌트에서 전송된 이벤트를 처리합니다."""
    if not isinstance(event_data, dict):
        # 유효하지 않은 이벤트 데이터 무시
        return
    
    event_type = event_data.get('type')
    payload = event_data.get('payload', {})

    # 1. 페이지 전환 이벤트 처리
    if event_type == 'NAVIGATE_TO':
        page = payload.get('page')
        if page in PAGE_FILES:
            st.session_state.current_page = page
            # st.rerun() 대신 Streamlit이 자연스럽게 상태를 업데이트하도록 합니다.
        else:
            st.warning(f"Warning: Page '{page}' is not defined.")
            
    # 2. 로그인 성공 이벤트 처리
    elif event_type == 'LOGIN_SUCCESS':
        st.session_state.current_page = PAGE_HOME # 홈 화면으로 전환 (추후 구현)
        st.session_state.user_data = payload.get('user')
        # st.rerun()

    # 3. 회원가입 성공 이벤트 처리
    elif event_type == 'SIGNUP_SUCCESS':
        # 회원가입 성공 후 로그인 페이지로 전환
        st.session_state.current_page = PAGE_LOGIN
        # st.rerun()

# --- 메인 앱 로직 ---

# 1. 사이드바 (회원가입/로그인 버튼)
st.sidebar.title("메뉴")
current_user_authenticated = (st.session_state.user_data is not None)

if not current_user_authenticated:
    # 사용자가 로그인하지 않은 상태일 때만 '회원가입' 버튼 표시
    if st.session_state.current_page == PAGE_LOGIN and st.sidebar.button("회원가입"):
        st.session_state.current_page = PAGE_SIGNUP
        
    elif st.session_state.current_page == PAGE_SIGNUP and st.sidebar.button("로그인 화면으로"):
        st.session_state.current_page = PAGE_LOGIN

# 2. 페이지 렌더링
st.title("잡스트레블링 (Job Traveling)")

page_file = PAGE_FILES.get(st.session_state.current_page)
html_content = read_html_file(page_file)

if html_content:
    # 1. JavaScript 변수 준비
    # Python 변수를 JSON 문자열로 직렬화하여 JavaScript에 안전하게 전달
    js_variables = f"""
        <script>
            window.__app_id = "{appId}";
            window.__firebase_config = JSON.parse('{FIREBASE_CONFIG_JSON_STRING.replace("'", "\\'")}')
        </script>
    """
    
    # 2. HTML 컴포넌트 렌더링
    try:
        component_value = st.components.v1.html(
            js_variables + html_content,
            height=600,
            scrolling=True,
            # 'key'와 'return_value' 인수는 Streamlit 버전에 따라 충돌하므로 제거합니다.
        )

        # 3. HTML 컴포넌트에서 반환된 값 처리
        # component_value가 유효한 딕셔너리(이벤트)일 때만 처리
        if isinstance(component_value, dict) and component_value:
            handle_html_event(component_value)
            
    except Exception as e:
        # 렌더링 중 발생할 수 있는 내부 오류 처리
        st.error(f"🚨 컴포넌트 렌더링 오류가 발생했습니다. 개발자에게 문의하십시오. 오류: {e}")

elif st.session_state.current_page == PAGE_HOME:
    st.write("메인 화면 (로그인 성공)")
    # 여기에 메인 화면 콘텐츠를 구현합니다.
    if st.button("로그아웃"):
        st.session_state.current_page = PAGE_LOGIN
        st.session_state.user_data = None
        # st.rerun()

# 로그 상태 디버깅 (선택 사항)
# st.sidebar.write("Debug Current Page:", st.session_state.current_page)
# st.sidebar.write("Debug User Data:", st.session_state.user_data)
