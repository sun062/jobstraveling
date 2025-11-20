import streamlit as st
import os
import json
from streamlit.components.v1 import html

# --- 상수 정의 ---
# GitHub 파일 구조(image_47d51e.png)에 따라 HTML 파일들이 저장된 하위 디렉토리 이름
HTML_DIR = "htmls"

# --- 유틸리티 함수 ---
def get_html_content(file_name):
    """HTML 파일을 읽어 내용을 반환합니다."""
    # os.path.join을 사용하여 'htmls' 디렉토리와 파일명을 결합하여 올바른 경로를 만듭니다.
    file_path = os.path.join(HTML_DIR, file_name)
    
    # ----------------------------------------------------
    # 경로 문제 해결을 위한 핵심 수정 부분
    # ----------------------------------------------------
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        # 경로를 명확히 보여주는 오류 메시지 추가
        st.error(f"❌ 오류: '{file_name}' 파일을 찾을 수 없습니다.")
        st.caption(f"시도된 경로: `{file_path}`")
        st.caption("🚨 'htmls' 디렉토리가 'app.py'와 같은 위치에 있는지 확인해주세요.")
        return None

def render_html(file_name, key):
    """지정된 HTML 파일을 스트림릿에 렌더링합니다."""
    html_content = get_html_content(file_name)
    if html_content:
        # 캔버스 환경에서 필요한 전역 변수를 HTML에 삽입
        auth_token = st.session_state.get('auth_token', '')
        # Firebase config는 실제 환경에서 자동으로 제공되지만, 로컬 테스트를 위해 빈 JSON을 사용합니다.
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
        html(full_html, height=800, scrolling=True, key=key)


# --- 네비게이션 및 세션 관리 ---

# 네비게이션 상태를 관리하는 함수
def navigate_to(page):
    st.session_state['current_page'] = page
    st.rerun()

# --- 메인 앱 로직 ---
if 'current_page' not in st.session_state:
    # 앱 시작 시 'login.html'이 먼저 뜨도록 설정
    st.session_state['current_page'] = 'login'

# Streamlit Component로부터 메시지를 수신하는 콜백 함수 (필요 시 구현)
def on_message_received(message):
    if message and 'type' in message and message['type'] == 'NAVIGATE':
        navigate_to(message['page'])

# 스트림릿 페이지 설정
st.set_page_config(layout="wide")

# 현재 페이지에 따라 HTML 파일 렌더링
page_map = {
    'login': 'login.html',
    'signup': 'signup.html',
    'forgot_password': 'forgot_password.html',
    'home': 'home.html', 
}

current_page_key = st.session_state['current_page']
html_file_name = page_map.get(current_page_key, 'login.html')

# UI 표시
st.title("💼 잡스트레블링 (Job-Trekking) 앱")
st.write(f"현재 로드 중인 페이지: **{current_page_key.upper()}**")

# HTML 파일 렌더링
render_html(html_file_name, key=current_page_key)

# --- 로컬 테스트용 네비게이션 버튼 (선택 사항) ---
st.sidebar.header("페이지 이동 (테스트용)")
if st.sidebar.button("로그인 페이지"):
    navigate_to('login')
if st.sidebar.button("홈 페이지"):
    navigate_to('home')
if st.sidebar.button("회원가입 페이지"):
    navigate_to('signup')
if st.sidebar.button("비밀번호 찾기"):
    navigate_to('forgot_password')
