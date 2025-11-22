import streamlit as st
from streamlit.components.v1 import html
import json

# --- 1. HTML Content Definitions (파이썬 문자열로 정의) ---

# Firebase 초기화 및 인증 로직을 위한 공통 JS 코드를 HTML <script> 부분에 추가합니다.
FIREBASE_INIT_JS = """
    // Firebase 초기화 및 인증 로직
    import { initializeApp } from "https://www.gstatic.com/firebasejs/11.6.1/firebase-app.js";
    import { getAuth, signInAnonymously, signInWithCustomToken } from "https://www.gstatic.com/firebasejs/11.6.1/firebase-auth.js";
    // Firestore에서 필요한 함수들을 모두 가져옵니다.
    import { getFirestore, collection, setDoc, doc, query, where, getDocs, setLogLevel } from "https://www.gstatic.com/firebasejs/11.6.1/firebase-firestore.js";
    
    let db;
    let auth;
    let userId; // 현재 세션의 Firebase 인증 UID (익명 사용자)
    let appId;
    let isFirebaseReady = false; // Firestore 준비 상태 플래그
    
    // Firestore 초기화 및 인증
    async function initializeFirebase() {
        try {
            // 필수 글로벌 변수 사용
            appId = typeof __app_id !== 'undefined' ? __app_id : 'default-app-id';
            const firebaseConfig = JSON.parse(typeof __firebase_config !== 'undefined' ? __firebase_config : '{}');
            const initialAuthToken = typeof __initial_auth_token !== 'undefined' ? __initial_auth_token : null;
            
            // 앱 초기화
            const app = initializeApp(firebaseConfig);
            db = getFirestore(app);
            auth = getAuth(app);
            setLogLevel('Debug'); // 디버깅을 위해 로그 레벨 설정
            
            // 인증
            if (initialAuthToken) {
                await signInWithCustomToken(auth, initialAuthToken);
            } else {
                // 토큰이 없거나 만료된 경우 익명 인증 시도
                await signInAnonymously(auth);
            }
            
            userId = auth.currentUser?.uid || crypto.randomUUID();
            isFirebaseReady = true; // 준비 완료
            console.log("Firebase initialized successfully. User ID:", userId);
            
            // 초기화 후 실행할 함수가 있다면 여기서 호출
            if (typeof onPageLoad === 'function') {
                onPageLoad(); 
            }

        } catch (error) {
            console.error("Firebase initialization or sign-in failed:", error);
        }
    }
    
    // 사용자 데이터 컬렉션 참조를 가져오는 함수
    // 공용 컬렉션을 사용하여 모든 사용자가 회원 정보를 조회할 수 있도록 합니다.
    function getUsersCollectionRef() {
        if (!isFirebaseReady) {
            console.error("Database not initialized.");
            return null;
        }
        // 공용 데이터 경로: /artifacts/{appId}/public/data/users
        const path = `artifacts/${appId}/public/data/users`; 
        return collection(db, path);
    }
    
    // 메시지 박스 관련 함수 (공통)
    function showMessage(text, action = null) {{
        const messageBox = document.getElementById('messageBox');
        const messageText = document.getElementById('messageText');
        
        messageText.textContent = text;
        window.nextAction = action; // 전역으로 관리
        if (messageBox) messageBox.classList.remove('hidden');
    }}

    function hideMessage() {{
        const messageBox = document.getElementById('messageBox');
        if (messageBox) messageBox.classList.add('hidden');
    }}
    
    function continueAction() {{
        hideMessage();
        if (typeof window.nextAction === 'function') {{
            window.nextAction(); 
            window.nextAction = null; 
        }}
    }}

    // Streamlit으로 페이지 전환 요청을 보내는 함수 (핵심)
    function requestStreamlitRedirect(pageName) {{
        parent.postMessage({{type: 'NAVIGATE', page: pageName}}, '*');
    }}

    // 페이지 로드 시 Firebase 초기화
    window.onload = initializeFirebase;
"""

# A. 로그인 화면 HTML (로그인 로직 구현)
LOGIN_HTML = f"""
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>잡스트레블링 - 로그인</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body {{ font-family: 'Inter', sans-serif; background-color: #f7f7f7; }}
        .input-field {{ width: 100%; padding: 10px; border: none; border-bottom: 2px solid #ddd; }}
        .input-field:focus {{ outline: none; border-bottom-color: #3b82f6; }}
        .login-button {{ background-color: #2563eb; transition: background-color 0.15s; }}
        .login-button:hover {{ background-color: #1d4ed8; }}
    </style>
</head>
<body class="p-4 sm:p-8 flex items-center justify-center min-h-screen">
    <div class="max-w-md w-full mx-auto bg-white p-6 sm:p-10 rounded-xl shadow-2xl space-y-6">
        <header class="text-center pb-4">
            <h1 class="text-3xl font-bold text-gray-800">잡스트레블링 로그인</h1>
            <p class="text-sm text-gray-500 mt-1">로그인 후 다양한 진로 체험 프로그램을 만나보세요.</p>
        </header>

        <form onsubmit="handleLogin(event)" class="space-y-4">
            <div>
                <label for="username" class="block font-medium text-gray-700">아이디</label>
                <input type="text" id="username" placeholder="아이디를 입력하세요" class="input-field" required>
            </div>
            <div>
                <label for="password" class="block font-medium text-gray-700">비밀번호</label>
                <input type="password" id="password" placeholder="비밀번호를 입력하세요" class="input-field" required>
            </div>
            
            <button type="submit" 
                    class="w-full py-3 mt-4 text-lg font-bold text-white login-button rounded-lg shadow-md transform hover:scale-[1.005]">
                로그인
            </button>
        </form>

        <div class="flex justify-center space-x-6 pt-4 text-sm">
            <a href="#" onclick="requestStreamlitRedirect('forgot_password')" 
               class="text-blue-500 hover:underline">비밀번호 찾기</a>
            <a href="#" onclick="requestStreamlitRedirect('signup')" 
               class="text-blue-500 hover:underline">회원가입</a>
        </div>
        
        <p class="text-xs text-gray-400 text-center pt-2">현재 UID: <span id="currentUid">로딩 중</span></p>
    </div>
    
    <!-- 메시지 박스 및 스크립트 -->
    <div id="messageBox" class="hidden fixed inset-0 bg-gray-600 bg-opacity-50 z-50 flex items-center justify-center p-4">
        <div class="bg-white p-6 rounded-lg shadow-xl max-w-sm w-full text-center">
            <p id="messageText" class="text-gray-800 font-medium mb-4">로그인 시도 중...</p>
            <button onclick="continueAction()" class="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition">확인</button>
        </div>
    </div>

    <script type="module">
        {FIREBASE_INIT_JS}

        function onPageLoad() {{
            document.getElementById('currentUid').textContent = userId;
        }}

        // 로그인 버튼 클릭 시 실행될 함수
        async function handleLogin(event) {{
            event.preventDefault();
            
            if (!isFirebaseReady) {{
                showMessage('데이터베이스 연결 중입니다. 잠시 후 다시 시도해 주세요.');
                return;
            }}

            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;

            showMessage('로그인 정보를 확인하고 있습니다...');
            
            try {{
                const usersRef = getUsersCollectionRef();
                
                // 1. 아이디와 비밀번호가 일치하는 사용자 찾기
                // 실제 앱에서는 비밀번호를 해시하여 비교해야 합니다.
                const q = query(usersRef, 
                    where("userId", "==", username),
                    where("password", "==", password)
                );
                
                const querySnapshot = await getDocs(q);
                
                if (querySnapshot.empty) {{
                    showMessage('아이디 또는 비밀번호가 올바르지 않습니다.');
                    return;
                }}

                // 2. 로그인 성공
                const userData = querySnapshot.docs[0].data();
                
                showMessage(`${userData.name}님, 환영합니다!`, () => {{
                    // Streamlit에 로그인 성공 메시지와 사용자 이름을 전달하여 상태를 home으로 변경
                    parent.postMessage({{
                        type: 'LOGIN_SUCCESS', 
                        page: 'home', 
                        username: userData.name
                    }}, '*');
                }});

            }} catch (error) {{
                console.error("로그인 중 Firestore 조회 오류:", error);
                showMessage(`로그인 중 오류가 발생했습니다: ${error.message}`);
            }}
        }}
    </script>
</body>
</html>
"""

# B. 회원가입 화면 HTML (경로 수정 포함)
SIGNUP_HTML = f"""
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>잡스트레블링 - 회원가입</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body {{ font-family: 'Inter', sans-serif; background-color: #f7f7f7; }}
        .input-field {{ width: 100%; padding: 10px; border: none; border-bottom: 1px solid #ddd; transition: border-bottom-color 0.15s ease-in-out; font-size: 16px; }}
        .input-field:focus {{ outline: none; border-bottom-color: #3b82f6; }}
        .input-label {{ display: block; font-weight: 600; color: #4b5563; margin-bottom: 4px; font-size: 14px; }}
        #signupButton:disabled {{ background-color: #9ca3af; cursor: not-allowed; transform: none; }}
    </style>
</head>
<body class="p-4 sm:p-8">
    <div class="max-w-xl mx-auto bg-white p-6 sm:p-10 rounded-xl shadow-2xl space-y-8">
        <header class="pb-4 border-b border-gray-200">
            <h1 class="text-3xl font-bold text-gray-800">회원가입</h1>
            <p class="text-sm text-gray-500 mt-1">* 필수정보입력</p>
        </header>

        <form id="signupForm" onsubmit="handleSignup(event)" class="space-y-6">
            <section class="space-y-4 border p-4 rounded-lg bg-blue-50/50">
                <h2 class="text-xl font-bold text-blue-700 mb-4">나의 학교 정보 입력 *</h2>
                
                <div class="flex items-center space-x-6">
                    <span class="input-label !mb-0 w-20">구분 *</span>
                    <div class="flex space-x-4">
                        <span class="px-3 py-1 bg-blue-600 text-white text-sm rounded-full font-semibold">학생</span>
                        <span class="px-3 py-1 bg-gray-200 text-gray-600 text-sm rounded-full">교사</span>
                    </div>
                </div>

                <div>
                    <div class="flex items-end space-x-2">
                        <div class="flex-grow">
                            <label for="school" class="input-label">학교 *</label>
                            <input type="text" id="school" name="school" placeholder="학교를 입력하거나 검색해 주세요." class="input-field border-b-2" required>
                        </div>
                        <button type="button" onclick="showMessage('학교 검색 기능 구현 예정')" class="flex-shrink-0 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition">학교 찾기</button>
                    </div>
                </div>

                <div class="grid grid-cols-3 gap-4">
                    <div>
                        <label for="grade" class="input-label">학년 *</label>
                        <select id="grade" name="grade" class="input-field border-b-2" required>
                            <option value="">선택</option><option value="1">1학년</option><option value="2">2학년</option><option value="3">3학년</option>
                        </select>
                    </div>
                    <div>
                        <label for="classNum" class="input-label">반 *</label>
                        <input type="number" id="classNum" name="classNum" placeholder="반" class="input-field border-b-2" required>
                    </div>
                    <div>
                        <label for="studentNum" class="input-label">번호 *</label>
                        <input type="number" id="studentNum" name="studentNum" placeholder="번호" class="input-field border-b-2" required>
                    </div>
                </div>
            </section>
            
            <section class="space-y-6">
                <div>
                    <label for="name" class="input-label">이름 *</label>
                    <input type="text" id="name" name="name" placeholder="이름을 입력하세요" class="input-field" required>
                </div>

                <div>
                    <label for="userId" class="input-label">아이디 *</label>
                    <div class="flex space-x-2">
                        <input type="text" id="userId" name="userId" placeholder="아이디" class="input-field flex-grow" required>
                        <button type="button" onclick="showMessage('아이디 중복확인 기능 구현 예정')" class="flex-shrink-0 px-4 py-2 bg-gray-300 text-gray-800 rounded-lg hover:bg-gray-400 transition text-sm">중복확인</button>
                    </div>
                </div>

                <div>
                    <label for="email" class="input-label">이메일 *</label>
                    <input type="email" id="email" name="email" placeholder="이메일 주소" class="input-field" required>
                </div>

                <div>
                    <label for="password" class="input-label">비밀번호 *</label>
                    <input type="password" id="password" name="password" placeholder="8자 이상 20자 이하" class="input-field" required onkeyup="checkPasswordMatch()">
                    <p class="text-xs text-gray-500 mt-1">✓ 8자 이상 20자 이하 (대소문자, 숫자, 특수문자 3개 조합 권장)</p>
                </div>

                <div>
                    <label for="passwordConfirm" class="input-label">비밀번호 확인 *</label>
                    <input type="password" id="passwordConfirm" name="passwordConfirm" placeholder="비밀번호 재확인" class="input-field" required onkeyup="checkPasswordMatch()">
                    <p id="passwordMatchMessage" class="text-xs mt-1 h-4"></p>
                </div>
                
                <div>
                    <label for="birthdate" class="input-label">생년월일 *</label>
                    <div class="relative">
                        <input type="date" id="birthdate" name="birthdate" class="input-field pr-10" required>
                        <span class="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 pointer-events-none">
                            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M6 2a1 1 0 00-1 1v1H4a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2h-1V3a1 1 0 00-1-1zm0 5a1 1 0 000 2h8a1 1 0 100-2H6z" clip-rule="evenodd" /></svg>
                        </span>
                    </div>
                </div>

            </section>
            
            <button type="submit" id="signupButton" class="w-full py-3 mt-8 text-xl font-bold text-white bg-blue-500 hover:bg-blue-600 rounded-lg shadow-md transition duration-150 ease-in-out transform hover:scale-[1.005] focus:outline-none focus:ring-4 focus:ring-blue-300" disabled>
                가입하기
            </button>
            
            <button type="button" onclick="redirectToLogin()" class="w-full py-3 text-base font-semibold text-gray-600 bg-gray-200 hover:bg-gray-300 rounded-lg transition duration-150 ease-in-out">
                취소 및 돌아가기
            </button>

        </form>

        <!-- 메시지 박스 -->
        <div id="messageBox" class="hidden fixed inset-0 bg-gray-600 bg-opacity-50 z-50 flex items-center justify-center p-4">
            <div class="bg-white p-6 rounded-lg shadow-xl max-w-sm w-full text-center">
                <p id="messageText" class="text-gray-800 font-medium mb-4"></p>
                <button onclick="continueAction()" id="messageBoxConfirmButton" class="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition">확인</button>
            </div>
        </div>
    </div>

    <script type="module">
        {FIREBASE_INIT_JS}

        let isPasswordMatched = false;

        function redirectToLogin() {{
             showMessage('로그인 화면으로 돌아갑니다.', () => {{
                 requestStreamlitRedirect('login');
             }});
        }}
        
        function checkPasswordMatch() {{
            const password = document.getElementById('password').value;
            const passwordConfirm = document.getElementById('passwordConfirm').value;
            const messageElement = document.getElementById('passwordMatchMessage');
            const signupButton = document.getElementById('signupButton');

            if (passwordConfirm.length === 0) {{
                messageElement.textContent = '';
                messageElement.className = 'text-xs mt-1 h-4';
                isPasswordMatched = false;
            }} else if (password === passwordConfirm) {{
                messageElement.textContent = '비밀번호가 일치합니다.';
                messageElement.className = 'text-xs mt-1 font-semibold text-green-600 h-4';
                isPasswordMatched = true;
            }} else {{
                messageElement.textContent = '비밀번호가 일치하지 않습니다.';
                messageElement.className = 'text-xs mt-1 font-semibold text-red-600 h-4';
                isPasswordMatched = false;
            }}
            
            signupButton.disabled = !isPasswordMatched; 
        }}

        // 회원가입 버튼 클릭 시 실행될 함수 (Firestore 연동 구현)
        async function handleSignup(event) {{
            event.preventDefault(); 
            
            if (!isPasswordMatched) {{
                showMessage('비밀번호 확인이 일치하지 않아 가입할 수 없습니다. 확인 후 다시 시도해 주세요.');
                return;
            }}
            
            if (!isFirebaseReady || !userId) {{
                showMessage('데이터베이스 연결 중이거나 인증에 실패했습니다. 잠시 후 다시 시도해 주세요.');
                return;
            }}
            
            const form = document.getElementById('signupForm');
            const formData = new FormData(form);
            const user_id = formData.get('userId'); 
            const password = formData.get('password'); 
            
            showMessage('회원 정보를 확인하고 있습니다...');
            
            try {{
                const usersRef = getUsersCollectionRef();
                
                // 1. 아이디 중복 확인 쿼리
                const q = query(usersRef, where("userId", "==", user_id));
                const querySnapshot = await getDocs(q);
                
                if (!querySnapshot.empty) {{
                    showMessage('이미 사용 중인 아이디입니다. 다른 아이디를 사용해 주세요.');
                    return;
                }}

                // 2. 새로운 사용자 데이터 객체 생성
                const userUID = doc(usersRef).id; // Firestore에서 새로운 문서 ID를 미리 생성 (Firebase Auth UID가 아님)
                const userData = {{
                    userDocId: userUID, // 문서 ID를 필드에 저장
                    userId: user_id,
                    password: password, 
                    name: formData.get('name'),
                    email: formData.get('email'),
                    birthdate: formData.get('birthdate'),
                    school: formData.get('school'),
                    grade: formData.get('grade'),
                    classNum: formData.get('classNum'),
                    studentNum: formData.get('studentNum'),
                    createdAt: new Date().toISOString()
                }};

                // 3. Firestore에 데이터 저장 (생성된 userUID를 문서 ID로 사용)
                await setDoc(doc(usersRef, userUID), userData);

                showMessage('회원가입이 완료되었습니다! 로그인 화면으로 이동합니다.', () => {{
                    requestStreamlitRedirect('login');
                }});
                
            }} catch (error) {{
                console.error("회원가입 중 Firestore 저장 오류:", error);
                showMessage(`회원가입 중 오류가 발생했습니다: ${error.message}`);
            }}
        }}
        
        function onPageLoad() {{
            document.getElementById('signupButton').disabled = true;
        }}
    </script>
</body>
</html>
"""

# C. 비밀번호 찾기 화면 HTML (Placeholder)
FORGOT_PASSWORD_HTML = f"""
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>잡스트레블링 - 비밀번호 찾기</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body {{ font-family: 'Inter', sans-serif; background-color: #f7f7f7; }}
        .input-field {{ width: 100%; padding: 12px; border: 1px solid #e5e7eb; border-radius: 8px; transition: border-color 0.15s ease-in-out; font-size: 16px; }}
        .input-field:focus {{ outline: none; border-color: #3b82f6; }}
        .input-label {{ display: block; font-weight: 500; color: #4b5563; margin-bottom: 4px; font-size: 14px; }}
        .search-button {{ padding: 12px 0; font-size: 18px; font-weight: 700; color: white; background-color: #10b981; border-radius: 8px; transition: background-color 0.15s; box-shadow: 0 4px 6px -1px rgba(16, 185, 129, 0.2), 0 2px 4px -2px rgba(16, 185, 129, 0.2); }}
        .search-button:hover {{ background-color: #059669; }}
    </style>
</head>
<body class="p-4 sm:p-8 flex items-center justify-center min-h-screen">
    <div class="max-w-md w-full mx-auto bg-white p-6 sm:p-10 rounded-xl shadow-2xl space-y-8">
        <header class="text-center pb-4">
            <h1 class="text-3xl font-bold text-gray-800">비밀번호 찾기</h1>
            <p class="text-sm text-gray-500 mt-2">회원 정보 확인을 위해 다음 정보를 입력해 주세요.</p>
        </header>

        <form id="forgotPasswordForm" onsubmit="handleFindPassword(event)" class="space-y-6">
            <section class="space-y-4 border p-4 rounded-lg bg-gray-50/50">
                <h2 class="text-lg font-semibold text-gray-700">나의 학교 정보</h2>
                <div>
                    <label for="school" class="input-label">학교 *</label>
                    <input type="text" id="school" name="school" placeholder="등록된 학교명을 입력하세요" class="input-field" required>
                </div>
                <div class="grid grid-cols-3 gap-3">
                    <div><label for="classNum" class="input-label">반 *</label><input type="number" id="classNum" name="classNum" placeholder="반" class="input-field" required></div>
                    <div><label for="studentNum" class="input-label">번호 *</label><input type="number" id="studentNum" name="studentNum" placeholder="번호" class="input-field" required></div>
                    <div><label class="input-label opacity-0">임시</label><div class="h-[44px]"></div></div>
                </div>
            </section>
            
            <section class="space-y-4">
                <h2 class="text-lg font-semibold text-gray-700">개인 정보</h2>
                <div><label for="name" class="input-label">이름 *</label><input type="text" id="name" name="name" placeholder="이름을 입력하세요" class="input-field" required></div>
                <div><label for="userId" class="input-label">아이디 *</label><input type="text" id="userId" name="userId" placeholder="아이디" class="input-field" required></div>
            </section>
            
            <button type="submit" class="w-full search-button mt-4">비밀번호 찾기</button>
        </form>

        <div class="text-center text-sm text-gray-500 pt-4 space-x-2">
            <a href="#" onclick="requestStreamlitRedirect('login')" class="hover:underline">로그인</a>
            <span>/</span>
            <a href="#" onclick="showMessage('아이디 찾기 화면으로 이동합니다. (구현 예정)')" class="hover:underline">아이디 찾기</a>
            <span>/</span>
            <a href="#" onclick="requestStreamlitRedirect('signup')" class="hover:underline">회원가입</a>
        </div>

        <!-- 메시지 박스 -->
        <div id="messageBox" class="hidden fixed inset-0 bg-gray-600 bg-opacity-50 z-50 flex items-center justify-center p-4">
            <div class="bg-white p-6 rounded-xl shadow-xl max-w-sm w-full text-center">
                <p id="messageText" class="text-gray-800 font-medium mb-4"></p>
                <div id="actionButtons" class="space-x-2">
                    <button onclick="continueAction()" id="messageBoxConfirmButton" class="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition">확인</button>
                    <button onclick="requestStreamlitRedirect('login')" id="loginRedirectButton" class="hidden px-4 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600 transition">로그인 화면으로 넘어가시겠습니까?</button>
                </div>
            </div>
        </div>
    </div>

    <script type="module">
        {FIREBASE_INIT_JS}
        
        async function handleFindPassword(event) {{
            event.preventDefault(); 
            
            if (!isFirebaseReady) {{
                showMessage('데이터베이스 연결 중입니다. 잠시 후 다시 시도해 주세요.');
                return;
            }}
            
            showMessage('비밀번호 찾기 기능 구현 예정: 다음 단계에서 Firestore에서 회원 정보를 조회하는 로직을 추가합니다.');
        }}
    </script>
</body>
</html>
"""

# D. 홈 화면 HTML (새로 생성)
HOME_HTML = f"""
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>잡스트레블링 - 홈</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body {{ 
            font-family: 'Inter', sans-serif; 
            background-color: #f0f4f8; 
            min-height: 100vh;
        }}
        .header-bg {{
            background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
        }}
        .program-card {{
            transition: transform 0.2s, box-shadow 0.2s;
        }}
        .program-card:hover {{
            transform: translateY(-4px);
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
        }}
    </style>
</head>
<body class="p-0">

    <!-- 1. 상단 헤더 및 검색 바 -->
    <header class="header-bg p-4 shadow-lg sticky top-0 z-10">
        <div class="max-w-4xl mx-auto flex justify-between items-center text-white">
            <h1 class="text-2xl font-bold">🗺️ Job-Trekking 홈</h1>
            <button onclick="requestStreamlitLogout()" class="text-sm px-3 py-1 bg-white bg-opacity-20 rounded-full hover:bg-opacity-30 transition">
                로그아웃
            </button>
        </div>
        
        <!-- 검색 입력 영역 -->
        <div class="max-w-4xl mx-auto mt-4">
            <div class="relative">
                <input type="text" id="regionSearch" onkeyup="filterPrograms()"
                       placeholder="지역 또는 프로그램명으로 검색하세요 (예: 서울, IT)" 
                       class="w-full p-3 pl-10 rounded-xl shadow-md text-gray-800 focus:ring-2 focus:ring-blue-300 focus:outline-none transition">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
            </div>
        </div>
    </header>

    <!-- 2. 프로그램 목록 -->
    <main class="max-w-4xl mx-auto p-4 sm:p-8">
        <h2 class="text-xl font-bold text-gray-800 mb-4">⭐ 오늘의 추천 프로그램</h2>
        
        <div id="programList" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            <!-- 프로그램 카드가 JS에 의해 여기에 삽입됩니다. -->
        </div>
    </main>

    <!-- 3. Footer (선택 사항) -->
    <footer class="text-center text-gray-500 text-sm py-6 border-t mt-10">
        © 2024 Job-Trekking | 모든 프로그램 정보는 주관사에 귀속됩니다.
    </footer>

    <script type="module">
        {FIREBASE_INIT_JS}

        // Mock 데이터: 견학 및 진로 프로그램 목록
        const MockPrograms = [
            {{ 
                id: 1, 
                title: "서울시 IT 미래 인재 캠프", 
                region: "서울", 
                type: "진로", 
                url: "https://www.naver.com",
                img: "https://placehold.co/400x200/4f46e5/ffffff?text=IT+Camp",
                description: "IT 기술 체험 및 현직자 멘토링 프로그램."
            }},
            {{ 
                id: 2, 
                title: "부산항만 공사 견학", 
                region: "부산", 
                type: "견학", 
                url: "https://www.google.com",
                img: "https://placehold.co/400x200/059669/ffffff?text=Port+Tour",
                description: "대한민국 최대 항만의 물류 흐름 체험."
            }},
            {{ 
                id: 3, 
                title: "경기 AI 로봇 체험관", 
                region: "경기", 
                type: "진로", 
                url: "https://www.daum.net",
                img: "https://placehold.co/400x200/f59e0b/ffffff?text=AI+Robot",
                description: "첨단 로봇 기술을 직접 만져보고 체험하는 기회."
            }},
            {{ 
                id: 4, 
                title: "광주 자동차 미래 산업 탐방", 
                region: "광주", 
                type: "견학", 
                url: "https://www.youtube.com",
                img: "https://placehold.co/400x200/dc2626/ffffff?text=Car+Industry",
                description: "친환경 자동차 생산 라인 및 연구소 방문."
            }},
            {{ 
                id: 5, 
                title: "강원 환경보호 교육 캠페인", 
                region: "강원", 
                type: "진로", 
                url: "https://www.naver.com",
                img: "https://placehold.co/400x200/10b981/ffffff?text=Eco+Camp",
                description: "지속 가능한 환경과 관련된 직업군 탐색."
            }},
        ];

        // 프로그램 카드를 생성하는 함수
        function createProgramCard(program) {{
            const card = document.createElement('a');
            card.href = program.url;
            card.target = "_blank"; // 새 창으로 열기
            card.className = "program-card bg-white rounded-xl shadow-lg overflow-hidden cursor-pointer block border border-gray-100 hover:border-blue-300";
            
            card.innerHTML = `
                <img src="${program.img}" onerror="this.onerror=null; this.src='https://placehold.co/400x200/cbd5e1/475569?text=Placeholder';" alt="${program.title}" class="w-full h-40 object-cover">
                <div class="p-4 space-y-2">
                    <span class="text-xs font-semibold px-2 py-0.5 rounded-full ${program.type === '진로' ? 'bg-indigo-100 text-indigo-700' : 'bg-green-100 text-green-700'}">${program.type}</span>
                    <h3 class="text-lg font-bold text-gray-800 truncate">${program.title}</h3>
                    <p class="text-sm text-gray-500">${program.description}</p>
                    <p class="text-xs text-gray-400 font-medium flex items-center">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.828 0l-4.243-4.243a8 8 0 1111.314 0z" /><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" /></svg>
                        ${program.region}
                    </p>
                </div>
            `;

            return card;
        }}

        // 프로그램 목록을 렌더링하는 함수
        function renderPrograms(programs) {{
            const container = document.getElementById('programList');
            if (!container) return;

            container.innerHTML = '';
            
            if (programs.length === 0) {{
                container.innerHTML = '<p class="col-span-full text-center text-gray-500 py-10">검색 결과가 없습니다. 다른 지역이나 키워드로 시도해 보세요.</p>';
                return;
            }}

            programs.forEach(program => {{
                container.appendChild(createProgramCard(program));
            }});
        }}

        // 검색 필터링 함수
        function filterPrograms() {{
            const query = document.getElementById('regionSearch').value.toLowerCase();
            
            const filtered = MockPrograms.filter(program => 
                program.region.toLowerCase().includes(query) ||
                program.title.toLowerCase().includes(query)
            );

            renderPrograms(filtered);
        }}
        
        // 로그아웃 버튼 클릭 시 Streamlit에 상태 변경 요청
        function requestStreamlitLogout() {{
             showMessage('로그아웃 되었습니다.', () => {{
                 parent.postMessage({{type: 'NAVIGATE', page: 'login'}}, '*');
             }});
        }}

        // 페이지 로드 시 전체 프로그램 렌더링
        function onPageLoad() {{
            filterPrograms();
        }}
    </script>
</body>
</html>
"""


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

# HTML 렌더링 함수
def render_html_page(html_content, key):
    """지정된 HTML 컨텐츠를 Streamlit에 렌더링하고, 높이를 자동 설정합니다."""
    
    # 홈 화면은 내용이 길어질 수 있으므로 높이를 더 크게 설정
    height = 1000 if key == 'home' else (650 if key == 'signup' else 500)
    html(html_content, height=height, scrolling=True)

# HTML에서 받은 메시지를 처리하는 리스너
def handle_message():
    """HTML iframe에서 전송된 메시지를 처리합니다."""
    try:
        # Streamlit Component의 "return_value"로 메시지를 받습니다.
        # Streamlit은 iframe에서 window.parent.postMessage를 통해 받은 데이터를 
        # 컴포넌트의 return_value로 제공합니다.
        
        # Streamlit에 컴포넌트 데이터를 받기 위한 빈 컴포넌트를 추가합니다.
        message = html("", height=0, key="message_listener", return_value=None)
        
        if message:
            # message는 딕셔너리 형태여야 합니다.
            # print("Received message:", message) # 디버깅용
            
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
    
    # 2. 페이지 상태에 따라 적절한 HTML을 렌더링
    st.markdown(f"**현재 상태:** `{st.session_state['page']}`", unsafe_allow_html=True)
    
    if st.session_state['page'] == 'login':
        render_html_page(LOGIN_HTML, 'login')
    elif st.session_state['page'] == 'signup':
        render_html_page(SIGNUP_HTML, 'signup')
    elif st.session_state['page'] == 'forgot_password':
        render_html_page(FORGOT_PASSWORD_HTML, 'forgot_password')
    elif st.session_state['page'] == 'home':
        st.title(f"환영합니다, {st.session_state['username']}님!")
        render_html_page(HOME_HTML, 'home')

# 사이드바 네비게이션 (개발 테스트용)
st.sidebar.title("페이지 네비게이션 (TEST)")
st.sidebar.caption("현재 로그인: " + st.session_state['username'])
if st.sidebar.button("로그인 화면"):
    set_page('login')
if st.sidebar.button("회원가입 화면"):
    set_page('signup')
if st.sidebar.button("비밀번호 찾기 화면"):
    set_page('forgot_password')
if st.sidebar.button("홈 화면 (로그인 필요 없음)"):
    st.session_state['username'] = 'TestUser' # 테스트를 위해 이름 설정
    set_page('home')

# 메인 앱 실행
main_app()

st.caption("✓ `LOGIN_HTML`에 Firestore 로그인 인증 로직이 추가되었으며, 성공 시 `HOME_HTML`이 렌더링됩니다. 홈 화면에서는 지역/키워드 검색 및 프로그램 카드를 확인할 수 있습니다.")
