import streamlit as st
import os
import json
from streamlit.components.v1 import html

# --- 상수 정의 ---
# HTML 파일들이 저장된 하위 디렉토리 이름
HTML_DIR = "htmls"

# app.py 파일이 있는 디렉토리의 절대 경로를 가져옵니다. 
# 이 방법이 Streamlit의 실행 환경 변화에 가장 안정적으로 대응합니다.
# BASE_DIR은 'app.py'가 있는 폴더의 경로입니다. 예: /Users/username/project/jobstraveling/
BASE_DIR = os.path.dirname(os.path.abspath(__file__)) 

# --- 유틸리티 함수 ---
def get_html_content(file_name):
    """HTML 파일을 읽어 내용을 반환합니다."""
    
    # BASE_DIR을 기준으로 'htmls' 디렉토리와 파일명을 결합하여 절대 경로를 만듭니다.
    file_path = os.path.join(BASE_DIR, HTML_DIR, file_name)
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        st.error(f"❌ 오류: '{file_name}' 파일을 찾을 수 없습니다.")
        st.caption(f"시도된 경로: `{file_path}`")
        st.caption("🚨 경로 문제가 지속되면, 'app.py'와 'htmls' 폴더가 같은 위치에 있는지 확인해주세요.")
        return None

def render_html(file_name, key):
    """지정된 HTML 파일을 스트림릿에 렌더링합니다."""
    html_content = get_html_content(file_name)
    if html_content:
        # 캔버스 환경에서 필요한 전역 변수를 HTML에 삽입
        # 현재 인증 토큰은 세션 상태에서 가져옵니다.
        auth_token = st.session_state.get('auth_token', '') 
        # Firebase config와 app ID는 환경에 따라 설정됩니다.
        firebase_config = json.dumps({}) 
        app_id = "job_trekking_app"

        # HTML에 JavaScript 변수 형태로 삽입
        script_vars = f"""
            <script>
                // Canvas 환경 변수를 설정합니다.
                const __initial_auth_token = "{auth_token}";
                const __firebase_config = '{firebase_config}';
                const __app_id = "{app_id}";
            </script>
        """
        
        full_html = script_vars + html_content
        
        # Streamlit에 HTML 렌더링
        # key는 페이지가 바뀔 때마다 컴포넌트를 새로 렌더링하는 데 도움을 줍니다.
        html(full_html, height=800, scrolling=True, key=key)


# --- 네비게이션 및 세션 관리 ---

# 네비게이션 상태를 관리하는 함수
def navigate_to(page):
    """지정된 페이지로 이동하고 Streamlit 앱을 다시 실행합니다."""
    st.session_state['current_page'] = page
    st.rerun()

# --- 메인 앱 로직 ---
if 'current_page' not in st.session_state:
    # 앱 시작 시 'login.html'이 먼저 뜨도록 설정
    st.session_state['current_page'] = 'login'

# Streamlit Component로부터 메시지를 수신하는 콜백 함수 (필요 시 구현)
# 현재는 사용되지 않지만, 향후 JavaScript 통신을 위해 남겨둡니다.
# def on_message_received(message):
#     if message and 'type' in message and message['type'] == 'NAVIGATE':
#         navigate_to(message['page'])

# 스트림릿 페이지 설정
st.set_page_config(layout="wide")

# 현재 페이지에 따라 HTML 파일 이름 매핑
page_map = {
    'login': 'login.html',
    'signup': 'signup.html',
    'forgot_password': 'forgot_password.html',
    'home': 'home.html', 
    # 필요한 다른 페이지들도 여기에 추가할 수 있습니다.
}

current_page_key = st.session_state['current_page']
# 매핑된 파일 이름이 없으면 기본값으로 'login.html'을 사용합니다.
html_file_name = page_map.get(current_page_key, 'login.html')

# UI 표시
st.title("💼 잡스트레블링 (Job-Trekking) 앱")
st.write(f"현재 로드 중인 페이지: **{current_page_key.upper()}**")

# HTML 파일 렌더링
render_html(html_file_name, key=current_page_key)

# --- 로컬 테스트용 네비게이션 버튼 ---
# 사이드바에 테스트용 페이지 이동 버튼을 추가합니다.
st.sidebar.header("페이지 이동 (테스트용)")
if st.sidebar.button("로그인 페이지"):
    navigate_to('login')
if st.sidebar.button("홈 페이지"):
    navigate_to('home')
if st.sidebar.button("회원가입 페이지"):
    navigate_to('signup')
if st.sidebar.button("비밀번호 찾기"):
    navigate_to('forgot_password')
