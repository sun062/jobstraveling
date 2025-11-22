import streamlit as st
from streamlit.components.v1 import html
import os
import json
import time

# --- 1. 환경 설정 및 상수 ---

# Canvas 환경 변수를 사용하여 앱 ID 및 인증 토큰 로드
APP_ID = os.getenv('__app_id', 'job_trekking_app')
INITIAL_AUTH_TOKEN = os.getenv('__initial_auth_token', None)

# 🚨🚨🚨 사용자님의 Firebase 설정 JSON 문자열이 여기에 반영되었습니다. 🚨🚨🚨
# 이 값은 이전에 Firebase 콘솔에서 복사한 config 객체입니다.
FIREBASE_CONFIG = '{"apiKey": "AIzaSyBiigw574H93Q1Ph5EJTUoJEhcbIBQAiqq", "authDomain": "jobstraveling-6f1c9.firebaseapp.com", "projectId": "jobstraveling-6f1c9", "storageBucket": "jobstraveling-6f1c9.appspot.com", "messagingSenderId": "159042468260", "appId": "1:159042468260:web:95c0008838407e9d1832931", "measurementId": "G-EL8FK8Y3WV"}'

# 페이지 이름 상수
PAGE_LOGIN = 'login'
PAGE_SIGNUP = 'signup'
PAGE_FORGOT_PASSWORD = 'forgot_password'
PAGE_HOME = 'home'

# 페이지 파일 경로 딕셔너리
PAGE_FILES = {
    PAGE_LOGIN: 'htmls/login.html',
    PAGE_SIGNUP: 'htmls/signup.html',
    PAGE_FORGOT_PASSWORD: 'htmls/forgot_password.html',
    PAGE_HOME: 'htmls/home.html',
}

# --- 2. HTML 로드 및 렌더링 함수 ---

def read_html_file(file_path):
    """지정된 경로의 HTML 파일 내용을 읽습니다."""
    try:
        # Streamlit 환경에서 파일 경로를 안전하게 처리하기 위해 os.path.join 사용
        base_dir = os.path.dirname(os.path.abspath(__file__))
        full_path = os.path.join(base_dir, file_path)
        
        with open(full_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        st.error(f"오류: '{file_path}' 파일을 찾을 수 없습니다.")
        st.info(f"시도된 경로: {full_path}")
        return None
    except Exception as e:
        st.error(f"파일 읽기 중 오류 발생: {e}")
        return None

def render_html(html_file_name, current_page_key):
    """HTML 파일을 렌더링하고 필요한 전역 변수를 주입합니다."""
    # 파일 내용을 읽어옵니다.
    html_content = read_html_file(html_file_name)
    
    if html_content is None:
        return

    # HTML 컴포넌트에 주입할 JavaScript 코드:
    # 1. Firebase Config와 Auth Token 주입
    # 2. Streamlit과의 통신을 위한 로직 (setComponentValue)
    js_variables = f"""
    <script>
        window.firebaseConfig = {FIREBASE_CONFIG};
        window.initialAuthToken = {json.dumps(INITIAL_AUTH_TOKEN)};
        
        // Streamlit으로 이벤트와 데이터를 다시 보내는 함수 (e.g., 로그인 성공, 페이지 이동)
        function sendToStreamlit(eventType, data = {{}}) {{
            // 이벤트 타입과 데이터를 포함하여 Streamlit 컴포넌트 값을 설정합니다.
            // key는 Streamlit에서 변화를 감지하는 데 사용됩니다.
            Streamlit.setComponentValue({{
                event: eventType,
                data: data,
                timestamp: Date.now() 
            }});
        }}
    </script>
    """
    
    # 최종 HTML 코드를 구성하여 Streamlit에 렌더링
    full_html = js_variables + html_content
    
    # key는 Streamlit 컴포넌트가 다시 렌더링될 때 상태를 유지하도록 돕습니다.
    # 현재 페이지 키를 key로 사용하면 페이지가 변경될 때 컴포넌트가 재설정됩니다.
    html(full_html, height=800, scrolling=True, key=current_page_key)


# --- 3. Streamlit 앱 상태 및 흐름 관리 ---

# 세션 상태 초기화
if 'current_page' not in st.session_state:
    st.session_state.current_page = PAGE_LOGIN
if 'is_authenticated' not in st.session_state:
    st.session_state.is_authenticated = False
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'auth_message' not in st.session_state:
    st.session_state.auth_message = None


def handle_html_event(value):
    """HTML 컴포넌트에서 받은 이벤트를 처리합니다."""
    if value and 'event' in value:
        event_type = value['event']
        data = value.get('data', {})
        st.session_state.auth_message = None # 이전 메시지 초기화
        
        st.info(f"HTML 이벤트 수신: {event_type}")

        if event_type == 'NAVIGATE_TO':
            # 페이지 이동 요청 처리
            target_page = data.get('page')
            if target_page in PAGE_FILES:
                st.session_state.current_page = target_page
            
        elif event_type == 'LOGIN_SUCCESS':
            # 로그인 성공 처리
            st.session_state.is_authenticated = True
            st.session_state.user_id = data.get('uid')
            st.session_state.auth_message = f"로그인 성공! 사용자 ID: {st.session_state.user_id}"
            st.session_state.current_page = PAGE_HOME
            
        elif event_type == 'LOGOUT_SUCCESS':
            # 로그아웃 성공 처리
            st.session_state.is_authenticated = False
            st.session_state.user_id = None
            st.session_state.auth_message = "로그아웃 되었습니다."
            st.session_state.current_page = PAGE_LOGIN

        elif event_type == 'AUTH_ERROR':
            # 인증 오류 처리
            st.session_state.auth_message = f"인증 오류: {data.get('message', '알 수 없는 오류')}"
        
        elif event_type == 'SIGNUP_SUCCESS':
            # 회원가입 성공 처리
            st.session_state.auth_message = f"회원가입 성공: {data.get('email', '')}. 로그인 페이지로 이동합니다."
            st.session_state.current_page = PAGE_LOGIN


# --- 4. 메인 앱 실행 ---

st.title("💼 잡스트레블링 (Job-Trekking) 앱")

# 인증 메시지 표시
if st.session_state.auth_message:
    if "오류" in st.session_state.auth_message:
        st.error(st.session_state.auth_message)
    else:
        st.success(st.session_state.auth_message)
        
st.markdown(f"**현재 로드 중인 페이지:** `{st.session_state.current_page.upper()}`")

# 현재 페이지의 HTML 파일 경로 가져오기
page_file = PAGE_FILES.get(st.session_state.current_page)

if page_file:
    # HTML 렌더링 및 Streamlit으로 값 반환 받기
    # ⚠️ component_value는 HTML 컴포넌트에서 sendToStreamlit() 함수로 보낸 값입니다.
    component_value = st.components.v1.html(
        read_html_file(page_file),
        height=800, 
        scrolling=True, 
        key=st.session_state.current_page,
        return_value=True # HTML에서 Python으로 값을 반환받도록 설정
    )
    
    # 반환된 값이 있으면 이벤트 처리 함수 호출
    if component_value:
        handle_html_event(component_value)
    
    # 렌더링된 페이지 표시
    st.markdown("---")
    st.write(f"이 페이지가 '{st.session_state.current_page}'를 보여줍니다.")
else:
    st.error(f"알 수 없는 페이지: {st.session_state.current_page}")

# 현재 상태 디버깅 정보 (옵션)
# st.sidebar.header("디버그 정보")
# st.sidebar.json(st.session_state)
