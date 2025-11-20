import streamlit as st
from streamlit.components.v1 import html
import json
import os

# --- 1. 파일 로드 및 HTML 렌더링 함수 ---

def load_html_content(filepath):
    """지정된 파일 경로에서 HTML 내용을 읽어 반환합니다."""
    try:
        # 파일이 현재 스크립트와 같은 디렉토리에 있다고 가정합니다.
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return f"<h1>오류: {filepath} 파일을 찾을 수 없습니다.</h1>"
    except Exception as e:
        return f"<h1>오류 발생: {e}</h1>"

def render_html_page(html_content, key):
    """지정된 HTML 컨텐츠를 Streamlit에 렌더링하고, 높이를 자동 설정합니다."""
    
    # 페이지 상태에 따라 높이를 조정합니다.
    if key == 'home':
        height = 1200  # 홈 화면은 내용이 길어질 수 있으므로 높이를 크게 설정
    elif key == 'signup':
        height = 800
    else:
        height = 650
        
    html(html_content, height=height, scrolling=True)

# --- 2. Streamlit App Logic (Python) ---

# Streamlit 세션 상태 초기화
if 'page' not in st.session_state:
    st.session_state['page'] = 'login'
if 'username' not in st.session_state:
    st.session_state['username'] = 'Guest'

# 페이지 전환 함수 (Streamlit 상태를 변경)
def set_page(page_name):
    """세션 상태를 변경하여 페이지를 전환합니다."""
    st.session_state['page'] = page_name

# HTML에서 받은 메시지를 처리하는 리스너
def handle_message():
    """HTML iframe에서 전송된 메시지를 처리합니다."""
    try:
        # Streamlit Component의 "return_value"로 메시지를 받습니다.
        message = html("", height=0, key="message_listener", return_value=None)
        
        if message:
            if message.get('type') == 'NAVIGATE':
                new_page = message.get('page')
                if new_page in ['login', 'signup', 'forgot_password', 'home']:
                    set_page(new_page)
                    
            elif message.get('type') == 'LOGIN_SUCCESS':
                st.session_state['username'] = message.get('username', 'User')
                set_page('home')
                
    except Exception as e:
        st.error(f"메시지 처리 오류: {e}")


# 메인 앱 실행 함수
def main_app():
    # 1. 메시지 리스너를 먼저 실행하여 페이지 전환 요청을 받습니다.
    handle_message() 
    
    # 2. 페이지 상태에 따라 적절한 HTML 파일을 읽고 렌더링
    
    current_page = st.session_state['page']
    
    # 파일 경로를 상태 이름에 맞게 설정
    page_files = {
        'login': 'login.html',
        'signup': 'signup.html',
        'forgot_password': 'forgot_password.html',
        'home': 'home.html',
    }
    
    filepath = page_files.get(current_page)
    
    if filepath:
        html_content = load_html_content(filepath)
        render_html_page(html_content, current_page)
    else:
        st.error(f"알 수 없는 페이지 상태: {current_page}")

# 사이드바 네비게이션 (개발 테스트용)
st.sidebar.title("페이지 네비게이션 (TEST)")
st.sidebar.caption("현재 로그인: " + st.session_state['username'])
if st.sidebar.button("로그인 화면"):
    set_page('login')
if st.sidebar.button("회원가입 화면"):
    set_page('signup')
if st.sidebar.button("비밀번호 찾기 화면"):
    set_page('forgot_password')
if st.sidebar.button("홈 화면 (로그인 테스트)"):
    st.session_state['username'] = '테스트 학생' # 테스트를 위해 이름 설정
    set_page('home')

# 메인 앱 실행
main_app()

st.caption("✓ `app.py`가 4개의 HTML 파일을 읽어 상태에 따라 렌더링합니다. HTML 파일들 내부에 모든 로직이 포함되어 있습니다.")
