import streamlit as st
from streamlit.components.v1 import html
import os
import json
import time

# --- 1. 환경 설정 및 상수 ---

# Canvas 환경 변수를 사용하여 앱 ID 및 인증 토큰 로드
APP_ID = os.getenv('__app_id', 'job_trekking_app')
INITIAL_AUTH_TOKEN = os.getenv('__initial_auth_token', None)

# 🚨🚨🚨 Firebase 설정 JSON 문자열을 안정적으로 파싱하여 Python 딕셔너리로 준비합니다. 🚨🚨🚨
FIREBASE_CONFIG_JSON_STRING = None
try:
    # 환경 변수 대신 직접 JSON 문자열을 사용
    config_str = '{"apiKey": "AIzaSyBiigw574H93Q1Ph5EJTUoJEhcbIBQAiqq", "authDomain": "jobstraveling-6f1c9.firebaseapp.com", "projectId": "jobstraveling-6f1c9", "storageBucket": "jobstraveling-6f1c9.appspot.com", "messagingSenderId": "159042468260", "appId": "1:159042468260:web:95c0008838407e9d1832931", "measurementId": "G-EL8FK8Y3WV"}'
    # JavaScript로 전달하기 위해 JSON 문자열 자체를 준비
    FIREBASE_CONFIG_JSON_STRING = config_str
except Exception:
    st.error("FATAL ERROR: Firebase Configuration string is invalid.")


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
    """지정된 경로의 HTML 파일 내용을 읽거나 오류 발생 시 None을 반환합니다."""
    try:
        # 현재 파일(app.py)의 디렉토리 경로를 기준으로 파일을 찾습니다.
        base_dir = os.path.dirname(os.path.abspath(__file__))
        full_path = os.path.join(base_dir, file_path)
        
        # 파일이 존재하는지 확인 (추가적인 디버깅 정보)
        if not os.path.exists(full_path):
            # 파일이 없으면 명확한 오류와 함께 None 반환
            st.error(f"❌ 오류: '{file_path}' 파일을 찾을 수 없습니다. 경로를 확인해주세요.")
            st.info(f"시도된 경로: {full_path}")
            return None

        with open(full_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        st.error(f"❌ 파일 읽기 중 오류: {e}")
        return None

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
    """상태만 업데이트하고, 렌더링은 Streamlit에 맡깁니다."""
    st.session_state.current_page = target_page
    if message is not None:
        st.session_state.auth_message = message
    if uid is not None:
        st.session_state.user_id = uid
    if is_auth is not None:
        st.session_state.is_authenticated = is_auth
        
    # 🚨🚨🚨 st.rerun()을 제거하여 불필요한 재실행을 막습니다.
    # st.rerun()


def handle_html_event(value):
    """HTML 컴포넌트에서 받은 이벤트를 처리합니다."""
    # 반환 값이 유효한 딕셔너리인지 확인하여 TypeError를 방지합니다.
    if isinstance(value, dict) and 'event' in value:
        event_type = value['event']
        data = value.get('data', {})
        
        if event_type == 'NAVIGATE_TO':
            target_page = data.get('page')
            if target_page in PAGE_FILES:
                st.session_state.auth_message = None 
                navigate(target_page)
                # 🚨🚨🚨 상태가 변경되었으므로 즉시 재실행
                st.rerun() 
            elif target_page is not None:
                st.error(f"⚠️ 페이지 전환 실패: 요청된 페이지 '{target_page}'는 PAGE_FILES에 정의되어 있지 않습니다.")
            
        elif event_type == 'LOGIN_SUCCESS':
            uid = data.get('uid')
            message = f"로그인 성공! 사용자 ID: {uid}"
            navigate(PAGE_HOME, message=message, uid=uid, is_auth=True)
            st.rerun()
            
        elif event_type == 'LOGOUT_SUCCESS':
            message = "로그아웃 되었습니다."
            navigate(PAGE_LOGIN, message=message, uid=None, is_auth=False)
            st.rerun()

        elif event_type == 'AUTH_ERROR':
            st.session_state.auth_message = f"인증 오류: {data.get('message', '알 수 없는 오류')}"
        
        elif event_type == 'SIGNUP_SUCCESS':
            # 회원가입 성공 시 메시지를 표시하고 로그인 페이지로 이동
            message = f"회원가입 성공: {data.get('email', '')}. 로그인 페이지로 이동합니다."
            navigate(PAGE_LOGIN, message=message)
            st.rerun()


# --- 4. 메인 앱 실행 ---

st.set_page_config(layout="wide")
st.title("💼 잡스트레블링 (Job-Trekking) 앱")

# 인증 메시지 표시 및 리셋
if st.session_state.auth_message:
    if "오류" in st.session_state.auth_message or "실패" in st.session_state.auth_message or "인증 오류" in st.session_state.auth_message:
        st.error(st.session_state.auth_message)
    else:
        st.success(st.session_state.auth_message)
    st.session_state.auth_message = None 
        
st.markdown(f"**현재 로드 중인 페이지:** `{st.session_state.current_page.upper()}`")

# 현재 페이지의 HTML 파일 경로 가져오기
page_file = PAGE_FILES.get(st.session_state.current_page)

# Firebase 설정 문자열이 유효할 때만 렌더링
if page_file and FIREBASE_CONFIG_JSON_STRING:
    # 안정적인 HTML 콘텐츠 로드 시도
    html_content = read_html_file(page_file)
    
    # html_content가 None이 아닐 경우에만 컴포넌트 렌더링
    if html_content is not None:
        # HTML 컴포넌트에 주입할 JavaScript 변수 설정
        js_variables = f"""
        <script>
            // Streamlit으로 이벤트와 데이터를 다시 보내는 함수
            function sendToStreamlit(eventType, data = {{}}) {{
                if (typeof Streamlit !== 'undefined' && Streamlit.setComponentValue) {{
                    Streamlit.setComponentValue({{
                        event: eventType,
                        data: data,
                        timestamp: Date.now() 
                    }});
                    // 🚨🚨🚨 이벤트 전송 후 프레임 높이를 다시 설정하여 Streamlit이 이벤트를 더 잘 포착하도록 유도
                    Streamlit.setFrameHeight(document.documentElement.scrollHeight); 
                }} else {{
                    console.error("Streamlit 객체가 준비되지 않았습니다. 이벤트를 보낼 수 없습니다.");
                }}
            }}
            
            // JSON 문자열로 주입됩니다.
            window.firebaseConfigJsonString = {json.dumps(FIREBASE_CONFIG_JSON_STRING)};
            window.initialAuthToken = {json.dumps(INITIAL_AUTH_TOKEN)};
            window.appId = {json.dumps(APP_ID)};

        </script>
        """
        
        try:
            # key 인수가 호환되지 않으므로 제거하고 렌더링
            component_value = st.components.v1.html(
                js_variables + html_content,
                height=800, 
                scrolling=True,
            )
            
            # 반환된 값이 유효한 딕셔너리일 때만 이벤트 처리 함수 호출
            if component_value and isinstance(component_value, dict):
                handle_html_event(component_value)
                
        except TypeError as e:
            st.error("🚨 컴포넌트 렌더링 오류 (TypeError): Streamlit과 HTML 컴포넌트 간 통신에 문제가 발생했습니다. 파라미터나 타입 정의를 확인해주세요.")
            st.code(f"Error details: {e}", language='python')
        except Exception as e:
             st.error(f"🚨 알 수 없는 렌더링 오류: {e}")
    else:
        # read_html_file에서 오류가 발생했을 경우
        pass 
    
else:
    if not FIREBASE_CONFIG_JSON_STRING:
         st.error("🚨 환경 설정 오류: Firebase 설정이 유효하지 않거나 비어 있습니다.")
    else:
        st.error(f"알 수 없는 페이지: {st.session_state.current_page}")
