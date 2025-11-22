import streamlit as st
from streamlit.components.v1 import html
import json
import time
import os

# --- 1. 상태 및 네비게이션 관리 ---

# 앱 ID 및 Firebase 설정 (캔버스 환경 변수 사용)
APP_ID = os.getenv('__app_id', 'job_trekking_app')
FIREBASE_CONFIG = os.getenv('__firebase_config', '{}')
INITIAL_AUTH_TOKEN = os.getenv('__initial_auth_token', None)

# 페이지 이름 상수
PAGE_LOGIN = 'login'
PAGE_HOME = 'home'

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'current_page' not in st.session_state:
    st.session_state.current_page = PAGE_LOGIN
if 'loading' not in st.session_state:
    st.session_state.loading = False

def navigate_to(page):
    """페이지 이동 상태를 설정하고 앱을 재실행합니다."""
    st.session_state.current_page = page
    st.rerun()

# --- 2. 컴포넌트 간 통신 (JavaScript -> Python) ---

def handle_js_message(message):
    """
    HTML 컴포넌트에서 postMessage로 전달된 데이터를 처리합니다.
    주로 인증 상태 변경이나 페이지 이동 요청을 처리합니다.
    """
    if not message:
        return

    # st.toast(f"메시지 수신: {message.get('type')}") # 디버깅용

    msg_type = message.get('type')

    if msg_type == 'LOGIN_SUCCESS':
        # 로그인 성공 시 사용자 ID와 인증 토큰을 세션에 저장합니다.
        st.session_state.user_id = message.get('userId')
        st.session_state.auth_token = message.get('authToken')
        st.session_state.logged_in = True
        st.session_state.loading = True
        
        # 로딩 상태를 보여주기 위해 잠시 대기
        time.sleep(0.5)
        st.session_state.loading = False
        
        # 홈 페이지로 이동합니다.
        navigate_to(PAGE_HOME)

    elif msg_type == 'LOGOUT':
        st.session_state.logged_in = False
        st.session_state.user_id = None
        st.session_state.auth_token = None
        navigate_to(PAGE_LOGIN)

    elif msg_type == 'NAVIGATE':
        target_page = message.get('page')
        if target_page in [PAGE_LOGIN, 'signup', 'forgot_password', PAGE_HOME]:
            navigate_to(target_page)
            
    elif msg_type == 'DB_OPERATION_RESULT':
        # 데이터베이스 작업 결과를 사용자에게 피드백합니다.
        st.toast(message.get('message'), icon="✅" if message.get('success') else "❌")


# --- 3. HTML/JS 컨텐츠 정의 ---

# Firebase 및 Tailwind CSS 로드
CORE_SCRIPTS = f"""
<script src="https://cdn.tailwindcss.com"></script>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
<style>
    body {{ font-family: 'Inter', sans-serif; background-color: #f7f9fb; }}
    .stApp {{ overflow-y: hidden !important; }}
    /* Tailwind CSS 설정을 위한 사용자 정의 */
    @layer components {{
        .card-shadow {{ box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.06); }}
    }}
</style>
<script type="module">
    // Firebase SDK 로드
    import {{ initializeApp }} from "https://www.gstatic.com/firebasejs/11.6.1/firebase-app.js";
    import {{ 
        getAuth, signInAnonymously, signInWithCustomToken, onAuthStateChanged, 
        createUserWithEmailAndPassword, signInWithEmailAndPassword, 
        sendPasswordResetEmail
    }} from "https://www.gstatic.com/firebasejs/11.6.1/firebase-auth.js";
    import {{ 
        getFirestore, doc, getDoc, setDoc, onSnapshot, collection, query, where, getDocs,
        serverTimestamp
    }} from "https://www.gstatic.com/firebasejs/11.6.1/firebase-firestore.js";
    
    // 파이썬에서 주입된 전역 변수
    const firebaseConfig = JSON.parse(window.__firebase_config || '{{}}');
    const appId = window.__app_id || 'default-app-id';
    const initialAuthToken = window.__initial_auth_token;

    // Firebase 초기화
    let app, auth, db;
    if (Object.keys(firebaseConfig).length > 0) {{
        app = initializeApp(firebaseConfig);
        auth = getAuth(app);
        db = getFirestore(app);
    }} else {{
        console.error("Firebase config is missing or invalid.");
    }}

    // UI에서 Python(Streamlit)으로 메시지 전송
    function sendStreamlitMessage(type, payload = {{}} ) {{
        if (window.parent) {{
            window.parent.postMessage({{
                type: type,
                ...payload
            }}, "*");
        }}
    }}
    
    // --- 인증 기능 구현 ---
    
    // 로그인 처리
    window.handleLogin = async (email, password) => {{
        if (!auth) {{ sendStreamlitMessage('DB_OPERATION_RESULT', {{ success: false, message: 'Firebase 인증 서비스가 초기화되지 않았습니다.' }}); return; }}
        try {{
            const userCredential = await signInWithEmailAndPassword(auth, email, password);
            const user = userCredential.user;
            sendStreamlitMessage('LOGIN_SUCCESS', {{ userId: user.uid, authToken: await user.getIdToken() }});
        }} catch (error) {{
            const message = error.message.includes('password') ? '비밀번호를 확인해주세요.' : '존재하지 않는 사용자입니다.';
            sendStreamlitMessage('DB_OPERATION_RESULT', {{ success: false, message: `로그인 실패: ${{message}}` }});
        }}
    }};
    
    // 회원가입 처리 (Placeholder - 실제 구현 시 데이터 저장 로직 추가 필요)
    window.handleSignup = async (email, password) => {{
        if (!auth) {{ sendStreamlitMessage('DB_OPERATION_RESULT', {{ success: false, message: 'Firebase 인증 서비스가 초기화되지 않았습니다.' }}); return; }}
        try {{
            const userCredential = await createUserWithEmailAndPassword(auth, email, password);
            
            // 사용자 프로필 문서 생성 (private data)
            const userId = userCredential.user.uid;
            const userDocRef = doc(db, `artifacts/${{appId}}/users/${{userId}}/profile`, 'info');
            
            await setDoc(userDocRef, {{ 
                email: email, 
                createdAt: serverTimestamp(),
                # 필요한 추가 정보 필드 (예: 이름, 닉네임)
            }});

            sendStreamlitMessage('DB_OPERATION_RESULT', {{ success: true, message: '회원가입에 성공했습니다. 로그인해주세요.' }});
            sendStreamlitMessage('NAVIGATE', {{ page: 'login' }});
        }} catch (error) {{
            let message = '회원가입 실패: ';
            if (error.code === 'auth/email-already-in-use') {{
                message += '이미 사용 중인 이메일입니다.';
            }} else if (error.code === 'auth/weak-password') {{
                message += '비밀번호가 너무 취약합니다 (6자 이상).';
            }} else {{
                message += error.message;
            }}
            sendStreamlitMessage('DB_OPERATION_RESULT', {{ success: false, message: message }});
        }}
    }};

    // 초기 인증 상태 확인 및 자동 로그인 (캔버스 환경)
    onAuthStateChanged(auth, (user) => {{
        if (user) {{
            // Custom Token으로 로그인하면 이미 인증된 상태이므로 추가 처리가 필요 없을 수 있음.
            // 필요하다면, 여기서 한번 더 상태를 확인하고 페이지를 이동시킵니다.
            if (!window.__auth_checked) {{
                // sendStreamlitMessage('LOGIN_SUCCESS', {{ userId: user.uid, authToken: user.getIdToken() }});
                // 이미 파이썬에서 상태를 관리하므로 중복 이벤트 방지
                window.__auth_checked = true;
            }}
        }} else {{
            // 초기 토큰이 있고 config가 있다면 Custom Token으로 로그인 시도
            if (initialAuthToken) {{
                signInWithCustomToken(auth, initialAuthToken).catch(err => {{
                    console.error("Custom token login failed:", err);
                    signInAnonymously(auth); // 익명 로그인 시도
                }});
            }} else {{
                // 초기 토큰이 없으면 익명 로그인 시도
                signInAnonymously(auth);
            }}
        }}
    }});

</script>
"""

# --- 로그인 페이지 HTML ---
LOGIN_HTML = f"""
{CORE_SCRIPTS}
<div class="min-h-screen flex items-center justify-center p-4">
    <div class="w-full max-w-md bg-white p-8 rounded-xl card-shadow">
        <h2 class="text-3xl font-bold text-center text-gray-800 mb-8">로그인</h2>
        <form onsubmit="event.preventDefault(); window.handleLogin(document.getElementById('email').value, document.getElementById('password').value);">
            <div class="mb-5">
                <label for="email" class="block text-sm font-medium text-gray-700 mb-1">이메일</label>
                <input type="email" id="email" required class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-indigo-500 focus:border-indigo-500 transition duration-150">
            </div>
            <div class="mb-6">
                <label for="password" class="block text-sm font-medium text-gray-700 mb-1">비밀번호</label>
                <input type="password" id="password" required class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-indigo-500 focus:border-indigo-500 transition duration-150">
            </div>
            <button type="submit" class="w-full bg-indigo-600 text-white py-2 rounded-lg font-semibold hover:bg-indigo-700 transition duration-200">로그인</button>
        </form>
        <div class="mt-6 text-center text-sm">
            <a href="#" onclick="sendStreamlitMessage('NAVIGATE', {{ page: 'forgot_password' }})" class="text-indigo-600 hover:text-indigo-800 transition duration-150 mr-4">비밀번호 찾기</a>
            <span class="text-gray-400">|</span>
            <a href="#" onclick="sendStreamlitMessage('NAVIGATE', {{ page: 'signup' }})" class="text-indigo-600 hover:text-indigo-800 transition duration-150 ml-4">회원가입</a>
        </div>
    </div>
</div>
"""

# --- 회원가입 페이지 HTML ---
SIGNUP_HTML = f"""
{CORE_SCRIPTS}
<div class="min-h-screen flex items-center justify-center p-4">
    <div class="w-full max-w-md bg-white p-8 rounded-xl card-shadow">
        <h2 class="text-3xl font-bold text-center text-gray-800 mb-8">회원가입</h2>
        <form onsubmit="event.preventDefault(); window.handleSignup(document.getElementById('signup-email').value, document.getElementById('signup-password').value);">
            <div class="mb-5">
                <label for="signup-email" class="block text-sm font-medium text-gray-700 mb-1">이메일</label>
                <input type="email" id="signup-email" required class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-indigo-500 focus:border-indigo-500 transition duration-150">
            </div>
            <div class="mb-5">
                <label for="signup-password" class="block text-sm font-medium text-gray-700 mb-1">비밀번호 (6자 이상)</label>
                <input type="password" id="signup-password" required minlength="6" class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-indigo-500 focus:border-indigo-500 transition duration-150">
            </div>
            <button type="submit" class="w-full bg-green-600 text-white py-2 rounded-lg font-semibold hover:bg-green-700 transition duration-200">가입하기</button>
        </form>
        <div class="mt-6 text-center text-sm">
            <a href="#" onclick="sendStreamlitMessage('NAVIGATE', {{ page: 'login' }})" class="text-indigo-600 hover:text-indigo-800 transition duration-150">로그인으로 돌아가기</a>
        </div>
    </div>
</div>
"""

# --- 비밀번호 찾기 페이지 HTML ---
FORGOT_PASSWORD_HTML = f"""
{CORE_SCRIPTS}
<div class="min-h-screen flex items-center justify-center p-4">
    <div class="w-full max-w-md bg-white p-8 rounded-xl card-shadow">
        <h2 class="text-3xl font-bold text-center text-gray-800 mb-8">비밀번호 찾기</h2>
        <p class="text-sm text-center text-gray-500 mb-6">등록된 이메일을 입력하시면 비밀번호 재설정 링크를 보내드립니다.</p>
        <form onsubmit="event.preventDefault(); window.handleResetPassword(document.getElementById('reset-email').value);">
            <div class="mb-5">
                <label for="reset-email" class="block text-sm font-medium text-gray-700 mb-1">이메일</label>
                <input type="email" id="reset-email" required class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-indigo-500 focus:border-indigo-500 transition duration-150">
            </div>
            <button type="submit" class="w-full bg-red-500 text-white py-2 rounded-lg font-semibold hover:bg-red-600 transition duration-200">비밀번호 재설정 링크 전송</button>
        </form>
        <div class="mt-6 text-center text-sm">
            <a href="#" onclick="sendStreamlitMessage('NAVIGATE', {{ page: 'login' }})" class="text-indigo-600 hover:text-indigo-800 transition duration-150">로그인으로 돌아가기</a>
        </div>
    </div>
</div>

<script>
    window.handleResetPassword = async (email) => {{
        if (!auth) {{ sendStreamlitMessage('DB_OPERATION_RESULT', {{ success: false, message: 'Firebase 인증 서비스가 초기화되지 않았습니다.' }}); return; }}
        try {{
            await sendPasswordResetEmail(auth, email);
            sendStreamlitMessage('DB_OPERATION_RESULT', {{ success: true, message: '비밀번호 재설정 이메일을 전송했습니다. 이메일을 확인해주세요.' }});
            sendStreamlitMessage('NAVIGATE', {{ page: 'login' }});
        }} catch (error) {{
            const message = error.code === 'auth/user-not-found' ? '해당 이메일로 등록된 사용자가 없습니다.' : error.message;
            sendStreamlitMessage('DB_OPERATION_RESULT', {{ success: false, message: `재설정 실패: ${{message}}` }});
        }}
    }};
</script>
"""

# --- 홈 페이지 HTML ---
# 가상 데이터 (실제 데이터는 Firestore에서 불러와야 함)
MOCK_PROGRAMS = [
    {
        "id": 1, 
        "title": "미래 기술 개발자 캠프", 
        "type": "진로", 
        "description": "AI, 로봇 공학 등 첨단 기술을 직접 체험하고 미래 직업을 탐색합니다.",
        "region": "서울", 
        "date": "2025-07-20",
        "progress": "접수 중",
    },
    {
        "id": 2, 
        "title": "공정 무역과 지속 가능한 경제 교육", 
        "type": "탐방", 
        "description": "공정 무역 기업을 방문하여 윤리적 소비와 글로벌 경제를 배웁니다.",
        "region": "부산", 
        "date": "2025-08-05",
        "progress": "마감 임박",
    },
    {
        "id": 3, 
        "title": "창업 마인드셋 워크숍", 
        "type": "진로", 
        "description": "실제 스타트업 창업가와 함께 아이디어를 구체화하고 사업 계획을 수립합니다.",
        "region": "경기", 
        "date": "2025-09-10",
        "progress": "접수 예정",
    },
]

# 프로그램 카드 템플릿 - 중괄호 이스케이프
PROGRAM_CARD_TEMPLATE = f"""
    <div class="bg-white p-4 rounded-xl card-shadow flex flex-col transition duration-300 hover:shadow-lg cursor-pointer" onclick="sendStreamlitMessage('DB_OPERATION_RESULT', {{ success: true, message: '프로그램 상세 보기 기능 (ID: {{program.id}})은 구현 예정입니다.' }})">
        <div class="flex justify-between items-start mb-2">
            <h3 class="text-lg font-bold text-gray-800 truncate">{{{{program.title}}}}</h3>
            
            <!-- 오류가 났던 라인: 중괄호 {{}}로 이스케이프 -->
            <span class="text-xs font-semibold px-2 py-0.5 rounded-full ${{program.type === '진로' ? 'bg-indigo-100 text-indigo-700' : 'bg-green-100 text-green-700'}}">{{{{program.type}}}}</span>
        </div>
        <p class="text-sm text-gray-600 mb-3 line-clamp-2">{{{{program.description}}}}</p>
        <div class="mt-auto flex justify-between items-center text-xs text-gray-500">
            <div class="flex items-center space-x-3">
                <span>📍 {{{{program.region}}}}</span>
                <span>📅 {{{{program.date}}}}</span>
            </div>
            <span class="font-semibold ${{program.progress === '접수 중' ? 'text-blue-500' : program.progress === '마감 임박' ? 'text-orange-500' : 'text-gray-400'}}">{{{{program.progress}}}}</span>
        </div>
    </div>
"""

# 프로그램 목록을 동적으로 생성하는 JavaScript - **PROGRAM_JS를 일반 문자열로 변경**
PROGRAM_JS = """
<script>
    const mockPrograms = JSON.parse('""" + json.dumps(MOCK_PROGRAMS) + """');
    const template = `""" + PROGRAM_CARD_TEMPLATE.replace('`', '\\`') + """`; // JS 템플릿 리터럴로 변환

    function renderPrograms() {
        const container = document.getElementById('program-list');
        if (!container) return;
        container.innerHTML = '';
        
        mockPrograms.forEach(program => {
            // EJS/Handlebars 스타일 대신, JS 템플릿 리터럴로 변환하여 렌더링
            let html = template;
            html = html.replace(/{{program.title}}/g, program.title);
            html = html.replace(/{{program.type}}/g, program.type);
            html = html.replace(/{{program.description}}/g, program.description);
            html = html.replace(/{{program.region}}/g, program.region);
            html = html.replace(/{{program.date}}/g, program.date);
            html = html.replace(/{{program.progress}}/g, program.progress);
            html = html.replace(/{{program.id}}/g, program.id);
            
            // 클래스 조건부 렌더링을 위한 정규식 치환
            const typeClass = program.type === '진로' ? 'bg-indigo-100 text-indigo-700' : 'bg-green-100 text-green-700';
            const progressClass = program.progress === '접수 중' ? 'text-blue-500' : program.progress === '마감 임박' ? 'text-orange-500' : 'text-gray-400';
            
            // 정규 표현식 자체를 문자열로 치환. 오류가 났던 정규식 패턴을 일반 문자열로 대체하여 파이썬 f-string 문제를 우회합니다.
            html = html.replace(/\\$\\{program.type === '진로' \\? 'bg-indigo-100 text-indigo-700' : 'bg-green-100 text-green-700'\\}/g, typeClass);
            html = html.replace(/\\$\\{program.progress === '접수 중' \\? 'text-blue-500' : program.progress === '마감 임박' \\? 'text-orange-500' : 'text-gray-400'\\}/g, progressClass);
            
            container.innerHTML += html;
        });
    }

    document.addEventListener('DOMContentLoaded', renderPrograms);
</script>
"""

HOME_HTML = f"""
{CORE_SCRIPTS}
{PROGRAM_JS}
<div class="min-h-screen p-6 bg-gray-50">
    <header class="flex justify-between items-center bg-white p-4 rounded-xl card-shadow mb-6">
        <h1 class="text-2xl font-bold text-gray-800">💼 Job-Trekking 홈</h1>
        <div class="flex items-center space-x-4">
            <span class="text-sm text-gray-600">환영합니다! (ID: {st.session_state.user_id if st.session_state.user_id else '익명'})</span>
            <button onclick="window.handleLogout()" class="bg-red-500 text-white text-sm px-3 py-1 rounded-lg hover:bg-red-600 transition duration-200">로그아웃</button>
        </div>
    </header>

    <main>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
            <!-- 1. 좌측 사이드바/프로필 요약 -->
            <div class="col-span-1">
                <div class="bg-white p-6 rounded-xl card-shadow mb-6">
                    <h3 class="text-xl font-semibold text-gray-800 mb-4">나의 정보</h3>
                    <div class="space-y-2 text-sm text-gray-600">
                        <p><strong>이메일:</strong> {st.session_state.user_id if st.session_state.user_id else '로그인 필요'}</p>
                        <p><strong>진로 관심사:</strong> IT, 금융</p>
                        <p><strong>등록 프로그램:</strong> 3건</p>
                    </div>
                    <button class="w-full mt-4 bg-indigo-500 text-white py-1.5 rounded-lg text-sm hover:bg-indigo-600 transition duration-200">프로필 수정</button>
                </div>
                
                <div class="bg-white p-6 rounded-xl card-shadow">
                    <h3 class="text-xl font-semibold text-gray-800 mb-4">나의 트레킹 기록</h3>
                    <ul class="text-sm space-y-2 text-gray-700">
                        <li class="flex justify-between items-center"><span>탐방 기록</span><span class="font-bold text-green-600">12건</span></li>
                        <li class="flex justify-between items-center"><span>뱃지 획득</span><span class="font-bold text-yellow-600">5개</span></li>
                        <li class="flex justify-between items-center"><span>최근 활동</span><span class="text-gray-500">2일 전</span></li>
                    </ul>
                </div>
            </div>

            <!-- 2. 중앙 메인 컨텐츠: 프로그램 목록 -->
            <div class="md:col-span-2">
                <div class="bg-white p-6 rounded-xl card-shadow mb-6">
                    <h3 class="text-xl font-semibold text-gray-800 mb-4">🚀 추천 프로그램</h3>
                    <div id="program-list" class="grid grid-cols-1 lg:grid-cols-2 gap-4">
                        <!-- 프로그램 카드가 JS에 의해 여기에 렌더링됩니다 -->
                        로딩 중...
                    </div>
                </div>

                <!-- 공지사항 및 이벤트 -->
                <div class="bg-white p-6 rounded-xl card-shadow">
                    <h3 class="text-xl font-semibold text-gray-800 mb-4">📢 공지사항</h3>
                    <ul class="text-sm space-y-2">
                        <li class="p-2 border-b last:border-b-0">시스템 안정화 점검 안내 (2025.06.30)</li>
                        <li class="p-2 border-b last:border-b-0">신규 탐방 프로그램 대규모 업데이트</li>
                    </ul>
                </div>
            </div>
        </div>
    </main>
</div>

<script>
    window.handleLogout = () => {{
        if (!auth) {{ sendStreamlitMessage('DB_OPERATION_RESULT', {{ success: false, message: '인증 서비스 오류.' }}); return; }}
        auth.signOut().then(() => {{
            sendStreamlitMessage('LOGOUT');
        }}).catch((error) => {{
            sendStreamlitMessage('DB_OPERATION_RESULT', {{ success: false, message: `로그아웃 실패: ${{error.message}}` }});
        }});
    }};
</script>
"""

# --- 4. 메인 스트림릿 앱 실행 로직 ---

st.set_page_config(layout="wide")
st.title("💼 잡스트레블링 (Job-Trekking) 앱")

# 현재 페이지에 따른 HTML 선택
page_html_map = {
    PAGE_LOGIN: LOGIN_HTML,
    'signup': SIGNUP_HTML,
    'forgot_password': FORGOT_PASSWORD_HTML,
    PAGE_HOME: HOME_HTML,
}

current_page = st.session_state.current_page
html_content = page_html_map.get(current_page, LOGIN_HTML)


# 로그인 상태에 따른 접근 제어
if not st.session_state.logged_in and current_page == PAGE_HOME:
    st.warning("로그인이 필요합니다.")
    navigate_to(PAGE_LOGIN)
    st.stop()
elif st.session_state.logged_in and current_page != PAGE_HOME:
    # 로그인했지만 홈이 아닌 경우, 홈으로 리디렉션
    navigate_to(PAGE_HOME)
    st.stop()
    
if st.session_state.loading:
    st.info("로그인 중입니다. 잠시 기다려 주세요...")
else:
    # Streamlit 컴포넌트 렌더링 및 메시지 수신
    # key 인수를 제거한 안정적인 렌더링 방식을 사용합니다.
    # on_render는 컴포넌트에서 postMessage가 발생했을 때 파이썬 함수를 호출합니다.
    component_result = html(
        html_content,
        height=800,
        scrolling=True,
    )

    # 컴포넌트로부터 수신된 메시지를 처리합니다.
    handle_js_message(component_result)

# --- 디버깅 및 테스트용 사이드바 ---
with st.sidebar:
    st.header("앱 상태 및 디버깅")
    st.write(f"**현재 페이지:** {st.session_state.current_page}")
    st.write(f"**로그인 상태:** {'✅' if st.session_state.logged_in else '❌'}")
    st.write(f"**사용자 ID:** {st.session_state.user_id}")
    
    st.header("페이지 이동 (테스트)")
    if st.button("홈으로 이동 (강제)"):
        navigate_to(PAGE_HOME)
    if st.button("로그인 페이지로 이동"):
        navigate_to(PAGE_LOGIN)
