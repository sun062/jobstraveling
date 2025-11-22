import streamlit as st
from streamlit.components.v1 import html
import os
import json
import time

# --- 1. 환경 설정 및 상수 ---

# Canvas 환경 변수를 사용하여 앱 ID 및 인증 토큰 로드
APP_ID = os.getenv('__app_id', 'job_trekking_app')
INITIAL_AUTH_TOKEN = os.getenv('__initial_auth_token', None)

# 🚨🚨🚨 Firebase 설정 JSON 문자열을 안정적으로 파싱 및 덤프합니다. 🚨🚨🚨
# 주입될 때는 최종적으로 JavaScript가 읽을 수 있는 안전한 문자열이 되어야 합니다.
try:
    FIREBASE_CONFIG_DICT = json.loads('{"apiKey": "AIzaSyBiigw574H93Q1Ph5EJTUoJEhcbIBQAiqq", "authDomain": "jobstraveling-6f1c9.firebaseapp.com", "projectId": "jobstraveling-6f1c9", "storageBucket": "jobstraveling-6f1c9.appspot.com", "messagingSenderId": "159042468260", "appId": "1:159042468260:web:95c0008838407e9d1832931", "measurementId": "G-EL8FK8Y3WV"}')
    # Python에서 최종 주입될 JSON 문자열을 준비 (js_variables에서 한 번 더 JSON.dumps로 감싸짐)
    FIREBASE_CONFIG_JSON = json.dumps(FIREBASE_CONFIG_DICT) 
except json.JSONDecodeError:
    st.error("FATAL ERROR: Firebase Configuration string is invalid JSON.")
    FIREBASE_CONFIG_JSON = "{}"


# 페이지 이름 상수
PAGE_LOGIN = 'login'
PAGE_SIGNUP = 'signup'
PAGE_HOME = 'home'

# 페이지 파일 경로 딕셔너리
PAGE_FILES = {
    PAGE_LOGIN: 'htmls/login.html',
    PAGE_SIGNUP: 'htmls/signup.html',
    PAGE_HOME: 'htmls/home.html',
}

# --- 2. HTML 로드 및 렌더링 함수 ---

def read_html_file(file_path):
    """지정된 경로의 HTML 파일 내용을 읽거나 오류 HTML을 반환합니다."""
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        full_path = os.path.join(base_dir, file_path)
        
        with open(full_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        # 파일이 없을 경우 안정적인 HTML 오류 페이지 반환
        error_html = f"""
        <div style="padding: 20px; background-color: #fdd; border: 1px solid #c00; border-radius: 8px; font-family: sans-serif;">
            <h3 style="color: #c00;">[파일 로드 오류]</h3>
            <p><strong>오류:</strong> '{file_path}' 파일을 찾을 수 없습니다. 경로를 확인해 주세요.</p>
        </div>
        """
        st.error(f"오류: '{file_path}' 파일을 찾을 수 없습니다. HTML 오류 페이지 로드.")
        return error_html
    except Exception as e:
        # 기타 파일 읽기 오류 시 안정적인 HTML 오류 페이지 반환
        error_html = f"""
        <div style="padding: 20px; background-color: #fdd; border: 1px solid #c00; border-radius: 8px; font-family: sans-serif;">
            <h3 style="color: #c00;">[파일 읽기 중 오류]</h3>
            <p><strong>오류:</strong> {e}</p>
        </div>
        """
        st.error(f"파일 읽기 중 오류 발생: {e}. HTML 오류 페이지 로드.")
        return error_html

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


def navigate(target_page, message=None, uid=None, is_auth=None):
    """상태를 업데이트하고 페이지를 변경합니다."""
    # 상태를 세션에 반영
    st.session_state.current_page = target_page
    if message is not None:
        st.session_state.auth_message = message
    if uid is not None:
        st.session_state.user_id = uid
    if is_auth is not None:
        st.session_state.is_authenticated = is_auth
        
    # 상태가 변경되었으므로 Streamlit을 재실행하여 새 페이지 렌더링
    st.rerun()


def handle_html_event(value):
    """HTML 컴포넌트에서 받은 이벤트를 처리합니다."""
    if value and 'event' in value:
        event_type = value['event']
        data = value.get('data', {})
        # st.session_state.auth_message = None # 메시지는 navigate에서 초기화되거나 덮어쓰여집니다.
        
        # 페이지 이동 요청 처리
        if event_type == 'NAVIGATE_TO':
            target_page = data.get('page')
            if target_page in PAGE_FILES:
                navigate(target_page)
            
        elif event_type == 'LOGIN_SUCCESS':
            # 로그인 성공 처리
            uid = data.get('uid')
            message = f"로그인 성공! 사용자 ID: {uid}"
            navigate(PAGE_HOME, message=message, uid=uid, is_auth=True)
            
        elif event_type == 'LOGOUT_SUCCESS':
            # 로그아웃 성공 처리
            message = "로그아웃 되었습니다."
            navigate(PAGE_LOGIN, message=message, uid=None, is_auth=False)

        elif event_type == 'AUTH_ERROR':
            # 인증 오류 처리
            # HTML에서 받은 오류 메시지는 navigate를 통하지 않고 바로 세션에 저장하여 다음 렌더링 시 표시합니다.
            st.session_state.auth_message = f"인증 오류: {data.get('message', '알 수 없는 오류')}"
        
        elif event_type == 'SIGNUP_SUCCESS':
            # 회원가입 성공 처리
            message = f"회원가입 성공: {data.get('email', '')}. 로그인 페이지로 이동합니다."
            navigate(PAGE_LOGIN, message=message)


# --- 4. 메인 앱 실행 ---

st.title("💼 잡스트레블링 (Job-Trekking) 앱")

# 인증 메시지 표시
# 메시지가 설정되어 있으면 표시하고, 다음 렌더링 시 중복 표시를 막기 위해 리셋합니다.
if st.session_state.auth_message:
    if "오류" in st.session_state.auth_message or "실패" in st.session_state.auth_message or "인증 오류" in st.session_state.auth_message:
        st.error(st.session_state.auth_message)
    else:
        st.success(st.session_state.auth_message)
    st.session_state.auth_message = None 
        
st.markdown(f"**현재 로드 중인 페이지:** `{st.session_state.current_page.upper()}`")

# 현재 페이지의 HTML 파일 경로 가져오기
page_file = PAGE_FILES.get(st.session_state.current_page)

if page_file:
    # 안정적인 HTML 콘텐츠 로드 시도
    html_content = read_html_file(page_file)
    
    if html_content:
        # HTML 컴포넌트에 주입할 JavaScript 변수 설정
        # Python에서 준비된 JSON 문자열을 다시 JSON.dumps로 감싸서,
        # HTML/JavaScript에서 안전한 문자열 리터럴로 주입되게 합니다.
        js_variables = f"""
        <script>
            // window.firebaseConfig는 JSON 문자열 리터럴로 주입되어 JS에서 JSON.parse가 필요합니다.
            window.firebaseConfig = JSON.parse({json.dumps(FIREBASE_CONFIG_JSON)}); 
            window.initialAuthToken = {json.dumps(INITIAL_AUTH_TOKEN)};
            window.appId = {json.dumps(APP_ID)};

            // Streamlit으로 이벤트와 데이터를 다시 보내는 함수
            function sendToStreamlit(eventType, data = {{}}) {{
                Streamlit.setComponentValue({{
                    event: eventType,
                    data: data,
                    timestamp: Date.now() 
                }});
            }}
        </script>
        """
        
        # Streamlit HTML 컴포넌트 렌더링
        # key를 current_page로 설정하여 페이지 변경 시 컴포넌트 강제 리로드 유도
        component_value = st.components.v1.html(
            js_variables + html_content,
            height=800, 
            scrolling=True, 
            key=f"html_comp_{st.session_state.current_page}", # 고유 키로 설정
            return_value=True
        )
        
        # 반환된 값이 있으면 이벤트 처리 함수 호출
        if component_value:
            handle_html_event(component_value)
    
else:
    st.error(f"알 수 없는 페이지: {st.session_state.current_page}")
