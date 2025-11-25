import streamlit as st
import streamlit.components.v1 as components
import json
import base64

# --- 0. Mock 데이터 및 상수 정의 ---
MOCK_PROGRAMS = [
    {"id": 1, "title": "서울시 IT 미래 인재 캠프", "region": "서울", "type": "진로", "url": "https://www.google.com/search?q=서울시+IT+캠프", "img": "https://placehold.co/400x200/4f46e5/ffffff?text=IT+Camp", "description": "IT 기술 체험 및 현직자 멘토링 프로그램.", "fields": ["AI/IT", "과학/기술"]},
]

REGIONS = ["전국", "서울", "부산", "대구", "인천", "광주", "대전", "울산", "세종", "경기", "강원", "충북", "충남", "전북", "전남", "경북", "경남", "제주"]
FIELDS = ["AI/IT", "생명/환경", "화학", "문학/언론", "예술/문화", "교육/보건", "금융/경제", "기계/제조", "운송/물류", "사회/인문", "과학/기술"]

# Base64 데이터를 삽입할 고유 플레이스홀더
BASE64_PLACEHOLDER = "__BASE64_DATA_TO_INSERT__"
SCRIPT_PLACEHOLDER = "__STREAMLIT_SCRIPT_TO_INSERT__"
PAGE_SCRIPT_PLACEHOLDER = "__PAGE_DATA_SCRIPT__"


# --- 1. 로그인 페이지 HTML 콘텐츠 (Base64 인코딩 대상) ---
def get_login_html_base64():
    """
    로그인 페이지 HTML을 Base64로 인코딩된 문자열 형태로 반환합니다.
    관리자 로그인 버튼을 추가했습니다.
    """
    # 템플릿 콘텐츠 (Raw String)
    html_content = r"""
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>로그인</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body { 
            font-family: 'Inter', sans-serif; 
            background-color: #f0f4f8; 
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            margin: 0;
            padding: 20px;
        }
        .login-card {
            background-color: white;
            padding: 2.5rem;
            border-radius: 1rem;
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
            max-width: 400px;
            width: 100%;
            text-align: center;
        }
    </style>
</head>
<body>
    <div id="login-container" class="login-card">
        <h1 class="text-4xl font-extrabold text-blue-600 mb-2">🗺️ Job-Trekking</h1>
        <p class="text-gray-500 mb-8">청소년을 위한 진로 체험 프로그램 검색 서비스</p>
        
        <div class="space-y-4 mb-6">
            <input type="text" placeholder="아이디 (선택 사항)" class="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500">
            <input type="password" placeholder="비밀번호 (선택 사항)" class="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500">
        </div>
        
        <button onclick="simulateLogin(false)" class="w-full py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 transition duration-150 shadow-lg transform hover:scale-[1.01] active:scale-[0.99]">
            일반 사용자 로그인 / 시작하기
        </button>

        <button onclick="simulateLogin(true)" class="w-full py-3 mt-3 bg-red-600 text-white font-semibold rounded-lg hover:bg-red-700 transition duration-150 shadow-lg transform hover:scale-[1.01] active:scale-[0.99]">
            🔒 관리자 로그인 (데모)
        </button>

        <p class="text-sm text-gray-400 mt-6">데모 버전: 실제 아이디/비밀번호는 필요하지 않습니다.</p>
    </div>

    <script>
        function simulateLogin(isAdmin) {
            // Streamlit Python 백엔드에 로그인 메시지를 보내 인증 상태를 변경하도록 요청
            parent.postMessage({ type: 'LOGIN', isAdmin: isAdmin }, '*');
        }
    </script>
</body>
</html>
    """
    # Base64 인코딩
    encoded_html = base64.b64encode(html_content.encode('utf-8')).decode('utf-8')
    return encoded_html

# --- 2. Base64 디코더 HTML 콘텐츠 (로그인 페이지 로드 스크립트) ---
def get_base64_decoder_html():
    """
    Base64 인코딩된 HTML을 디코딩하여 현재 Streamlit 컴포넌트에 삽입하는
    HTML 스크립트를 반환합니다. (Python 포맷팅 충돌 완전 회피)
    """
    encoded_content = get_login_html_base64()
    
    # 디코더 템플릿
    decoder_template = r"""
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <title>Decoder</title>
</head>
<body>
    <div id="loading-message" style="text-align: center; margin-top: 50px;">로그인 페이지 로딩 중...</div>
    <script>
        const encoded = '__BASE64_DATA_TO_INSERT__'; 
        
        function decodeBase64(base64) {
            const binary_string = window.atob(base64);
            const len = binary_string.length;
            const bytes = new Uint8Array(len);
            for (let i = 0; i < len; i++) {
                bytes[i] = binary_string.charCodeAt(i);
            }
            return new TextDecoder().decode(bytes);
        }

        try {
            const decodedHtml = decodeBase64(encoded);
            document.open();
            document.write(decodedHtml);
            document.close();
        } catch(e) {
            const msgEl = document.getElementById('loading-message');
            if (msgEl) {
                msgEl.style.color = 'red';
                msgEl.textContent = '페이지 로딩 오류. 콘솔을 확인해주세요.';
            }
            console.error("Base64 decoding failed:", e);
        }
    </script>
</body>
</html>
"""
    
    # Base64 데이터를 플레이스홀더에 직접 삽입
    final_html = decoder_template.replace(BASE64_PLACEHOLDER, encoded_content)
    
    # JS 중괄호를 이중 중괄호로 이스케이프하여 Python 포맷팅 충돌 회피
    return final_html.replace('{', '{{').replace('}', '}}')

# --- 3. HTML 콘텐츠 (홈 템플릿) 로드 ---
def get_base_home_html_content(is_admin):
    """Streamlit 세션 상태에 저장할 기본 HTML 템플릿을 반환합니다. """
    
    # 관리자 링크 HTML 조각
    admin_link = ""
    if is_admin:
        admin_link = """
        <button onclick="navigate('admin_add')" class="text-sm px-3 py-1 bg-white bg-opacity-20 rounded-full hover:bg-opacity:30 transition">
            관리자 페이지
        </button>
        """

    # Home Page HTML 템플릿 (Raw String)
    html = f"""
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>잡스트레블링 - 홈</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        /* (기존 CSS 스타일 유지) */
        body {{ 
            font-family: 'Inter', sans-serif; 
            background-color: #f0f4f8; 
            min-height: 100vh; 
            margin: 0;
            padding: 0;
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
        .tag-active {{
            background-color: #2563eb; /* Blue 700 */
            color: white;
            border-color: #2563eb;
        }}
        .tag-inactive {{
            background-color: #e0f2f7; /* Light Cyan */
            color: #0c4a6e; /* Cyan 900 */
            border-color: #bae6fd; /* Cyan 200 */
        }}
    </style>
</head>
<body class="p-0">

    <!-- 1. 상단 헤더 및 검색 바 -->
    <header class="header-bg p-4 shadow-lg sticky top-0 z-10">
        <div class="max-w-4xl mx-auto flex justify-between items-center text-white">
            <h1 class="text-2xl font-bold">🗺️ Job-Trekking 홈</h1>
            <div class="flex space-x-3">
                {admin_link}
                <button onclick="requestStreamlitLogout()" class="text-sm px-3 py-1 bg-white bg-opacity-20 rounded-full hover:bg-opacity:30 transition">
                    로그아웃
                </button>
            </div>
        </div>
        
        <!-- 선택형 검색 입력 영역 (생략) -->
        <div class="max-w-4xl mx-auto mt-4 grid grid-cols-2 gap-3">
            <!-- 기존의 지역/분야 선택 박스 내용... -->
            <div id="regionSelectBox" onclick="showRegionModal()" 
                 class="p-3 bg-white rounded-xl shadow-md text-gray-800 cursor-pointer flex items-center justify-between transition hover:ring-2 hover:ring-blue-300">
                <span id="selectedRegionText" class="truncate font-medium text-gray-600">지역 선택 (필수)</span>
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                </svg>
            </div>
            <div id="fieldSelectBox" onclick="showFieldModal()" 
                 class="p-3 bg-white rounded-xl shadow-md text-gray-800 cursor-pointer flex items-center justify-between transition hover:ring-2 hover:ring-blue-300">
                <span id="selectedFieldText" class="truncate font-medium text-gray-600">분야 선택 (다중 선택 가능)</span>
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                </svg>
            </div>
        </div>

        <div class="max-w-4xl mx-auto mt-3 flex justify-between items-center">
             <div id="currentFilters" class="text-sm text-white font-light">
                 <!-- 필터 내용... -->
             </div>
             <button onclick="resetFilters()" class="text-sm px-3 py-1 bg-white bg-opacity-20 rounded-full hover:bg-opacity:30 transition text-white">
                 초기화
             </button>
        </div>
    </header>

    <!-- 2. 프로그램 목록 -->
    <main class="max-w-4xl mx-auto p-4 sm:p-8">
        <h2 class="text-xl font-bold text-gray-800 mb-4">⭐ 프로그램 검색 결과</h2>
        
        <div id="programList" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            <!-- 프로그램 카드가 JS에 의해 여기에 삽입됩니다. -->
        </div>
    </main>

    <!-- 3. Footer / Modals (생략) -->
    <footer class="text-center text-gray-500 text-sm py-6 border-t mt-10">
        © 2024 Job-Trekking | 모든 프로그램 정보는 주관사에 귀속됩니다.
    </footer>
    
    <!-- 메시지 박스, 지역/분야 모달은 생략하고 JS로만 처리 -->

    <script type="module">
        import {{ initializeApp }} from "https://www.gstatic.com/firebasejs/11.6.1/firebase-app.js";
        import {{ getAuth, signInAnonymously, signInWithCustomToken }} from "https://www.gstatic.com/firebasejs/11.6.1/firebase-auth.js";
        import {{ getFirestore, setLogLevel }} from "https://www.gstatic.com/firebasejs/11.6.1/firebase-firestore.js";
        
        let db;
        let auth;
        let userId; 
        let appId;
        let isFirebaseReady = false; 
        
        let Programs = []; 
        let Regions = []; 
        let Fields = []; 

        let currentRegion = ""; 
        let currentFields = []; 
        
        // --- Firebase 초기화 함수 ---
        async function initializeFirebase() {{
            try {{
                // (Firebase 초기화 및 인증 로직은 그대로 유지)
                appId = typeof __app_id !== 'undefined' ? __app_id : 'default-app-id';
                const firebaseConfig = JSON.parse(typeof __firebase_config !== 'undefined' ? __firebase_config : '{{}}');
                const initialAuthToken = typeof __initial_auth_token !== 'undefined' ? __initial_auth_token : null;
                
                const app = initializeApp(firebaseConfig);
                db = getFirestore(app);
                auth = getAuth(app);
                setLogLevel('Debug');
                
                if (initialAuthToken) {{
                    await signInWithCustomToken(auth, initialAuthToken);
                }} else {{
                    await signInAnonymously(auth);
                }}
                
                userId = auth.currentUser?.uid || crypto.randomUUID();
                isFirebaseReady = true; 
                console.log("Firebase initialized successfully. User ID:", userId);
                
                if (typeof onPageLoad === 'function') {{
                    onPageLoad(); 
                }}

            }} catch (error) {{
                console.error("Firebase initialization or sign-in failed:", error);
                // showMessage("Firebase 초기화 중 오류가 발생했습니다.");
            }}
        }}

        // --- Navigation Function ---
        window.navigate = function(page) {{
            parent.postMessage({{ type: 'NAVIGATE', page: page }}, '*');
        }};

        // --- Streamlit Back-end Communication ---
        function requestInitialData() {{
            parent.postMessage({{ type: 'GET_INITIAL_DATA' }}, '*');
        }}

        window.requestStreamlitLogout = function() {{
            // showMessage('로그아웃 하시겠습니까?', () => {{
                 parent.postMessage({{type: 'LOGOUT'}}, '*');
            // }});
        }}

        window.addEventListener('message', (event) => {{
            if (event.source !== window.parent) return;

            const data = event.data;
            if (typeof data !== 'object' || data === null) return;

            switch (data.type) {{
                case 'PROGRAM_DATA':
                    Programs = data.programs || [];
                    Regions = data.regions || [];
                    Fields = data.fields || [];
                    
                    // createRegionOptions(); // 모달 생략
                    // createFieldOptions(); // 모달 생략
                    filterPrograms();
                    break;
                case 'ERROR_MESSAGE':
                    // showMessage(data.message || '알 수 없는 오류가 발생했습니다.');
                    console.error("Streamlit Error:", data.message);
                    break;
                default:
                    break;
            }}
        }});
        
        window.onload = initializeFirebase;
        
        // --- Program Filtering and Rendering (간소화) ---
        
        function createProgramCard(program) {{
            const card = document.createElement('a');
            card.href = program.url; 
            card.target = "_blank"; 
            card.className = "program-card bg-white rounded-xl shadow-lg overflow-hidden cursor-pointer block border border-gray-100 hover:border-blue-300";
            
            const typeColor = program.type === '진로' ? 'bg-indigo-100 text-indigo-700' : 'bg-green-100 text-green-700';

            const fieldTags = (program.fields || []).map(field => 
                `<span class="text-xs font-light px-2 py-0.5 rounded-full bg-gray-100 text-gray-600">${{field}}</span>`
            ).join('');

            card.innerHTML = `
                <img src="${{program.img}}" onerror="this.onerror=null; this.src='https://placehold.co/400x200/cbd5e1/475569?text=Image+Not+Found';" alt="${{program.title}}" class="w-full h-40 object-cover">
                <div class="p-4 space-y-2">
                    <div class="flex items-center space-x-2">
                        <span class="text-xs font-semibold px-2 py-0.5 rounded-full ${{typeColor}}">${{program.type}}</span>
                        ${{fieldTags}}
                    </div>
                    <h3 class="text-lg font-bold text-gray-800 truncate">${{program.title}}</h3>
                    <p class="text-sm text-gray-500">${{program.description}}</p>
                    <p class="text-xs text-gray-400 font-medium flex items-center">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.828 0l-4.243-4.243a8 8 0 1111.314 0z" /><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" /></svg>
                        ${{program.region}}
                    </p>
                </div>
            `;

            return card;
        }}

        function renderPrograms(programs) {{
            const container = document.getElementById('programList');
            if (!container) return;

            container.innerHTML = '';
            
            if (programs.length === 0) {{
                container.innerHTML = '<p class="col-span-full text-center text-gray-500 py-10">현재 조건에 맞는 프로그램이 없습니다.</p>';
                return;
            }}

            programs.forEach(program => {{
                container.appendChild(createProgramCard(program));
            }});
        }}
        
        window.filterPrograms = function() {{
            // 필터링 로직 생략하고 전체 프로그램 렌더링
            renderPrograms(Programs);
            updateFilterDisplay();
        }}

        function updateFilterDisplay() {{
            document.getElementById('selectedRegionText').textContent = "전체 지역 (데모)";
            document.getElementById('selectedFieldText').textContent = "전체 분야 (데모)";
            document.getElementById('currentFilters').innerHTML = `
                현재 필터: <span class="font-bold">전체</span>
            `;
        }}

        window.resetFilters = function() {{
            // showMessage('검색 조건이 초기화되었습니다.');
            filterPrograms();
        }}

        window.onPageLoad = function() {{
            requestInitialData();
            updateFilterDisplay();
        }}
        
        // 모달 함수들은 데모를 위해 비워둡니다.
        window.showRegionModal = function() {{}};
        window.hideRegionModal = function() {{}};
        window.showFieldModal = function() {{}};
        window.applyFieldSelection = function() {{}};

        updateFilterDisplay();

    </script>
    {PAGE_SCRIPT_PLACEHOLDER}
</body>
</html>
"""
    # JS 중괄호를 이중 중괄호로 이스케이프하여 Python 포맷팅 충돌 회피
    return html.replace('{', '{{').replace('}', '}}')

# --- 4. HTML 콘텐츠 (관리자 프로그램 추가 폼) ---
def get_admin_add_program_html_content():
    """관리자 페이지: 프로그램 추가 폼 HTML 콘텐츠를 반환합니다."""

    # Admin Add Program HTML 템플릿 (Raw String)
    html = f"""
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>프로그램 추가</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body {{ 
            font-family: 'Inter', sans-serif; 
            background-color: #f0f4f8; 
            min-height: 100vh; 
            margin: 0;
            padding: 0;
        }}
    </style>
</head>
<body class="p-4 sm:p-8">
    <div class="max-w-3xl mx-auto bg-white p-6 sm:p-8 rounded-xl shadow-2xl border border-blue-100">
        
        <header class="mb-8 border-b pb-4 flex justify-between items-center">
            <h1 class="text-3xl font-extrabold text-blue-700">🔒 새 진로 프로그램 추가</h1>
            <button onclick="navigate('home')" class="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition text-sm font-medium">
                홈으로 돌아가기
            </button>
        </header>

        <form id="programForm" onsubmit="event.preventDefault(); submitProgram();" class="space-y-6">
            
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <!-- 1. 프로그램 제목 -->
                <div>
                    <label for="title" class="block text-sm font-medium text-gray-700 mb-1">프로그램 제목 <span class="text-red-500">*</span></label>
                    <input type="text" id="title" required class="w-full p-3 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500">
                </div>

                <!-- 2. 프로그램 구분 -->
                <div>
                    <label for="type" class="block text-sm font-medium text-gray-700 mb-1">구분 <span class="text-red-500">*</span></label>
                    <select id="type" required class="w-full p-3 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500">
                        <option value="진로">진로 체험</option>
                        <option value="견학">현장 견학</option>
                        <option value="특강">온라인 특강</option>
                    </select>
                </div>
            </div>

            <!-- 3. 프로그램 상세 설명 -->
            <div>
                <label for="description" class="block text-sm font-medium text-gray-700 mb-1">상세 설명 <span class="text-red-500">*</span></label>
                <textarea id="description" rows="3" required class="w-full p-3 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500"></textarea>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <!-- 4. 프로그램 지역 -->
                <div>
                    <label for="region" class="block text-sm font-medium text-gray-700 mb-1">지역 <span class="text-red-500">*</span></label>
                    <select id="region" required class="w-full p-3 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500">
                        <!-- 지역 옵션은 JS로 채워집니다 -->
                    </select>
                </div>

                <!-- 5. 외부 URL -->
                <div>
                    <label for="url" class="block text-sm font-medium text-gray-700 mb-1">외부 신청 URL</label>
                    <input type="url" id="url" placeholder="https://..." class="w-full p-3 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500">
                </div>
            </div>

            <!-- 6. 대표 이미지 URL -->
            <div>
                <label for="img" class="block text-sm font-medium text-gray-700 mb-1">대표 이미지 URL</label>
                <input type="url" id="img" placeholder="https://placehold.co/400x200" class="w-full p-3 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500">
                <p class="mt-1 text-xs text-gray-500">프로그램 카드에 표시될 이미지입니다.</p>
            </div>

            <!-- 7. 분야 태그 (다중 선택) -->
            <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">관련 분야 (다중 선택 가능) <span class="text-red-500">*</span></label>
                <div id="fieldTagsContainer" class="flex flex-wrap gap-2 p-3 border border-gray-300 rounded-lg bg-gray-50">
                    <!-- 분야 태그 버튼들이 여기에 JS로 삽입됩니다. -->
                </div>
            </div>

            <div id="messageDisplay" class="p-3 text-sm rounded-lg text-center font-medium hidden"></div>

            <button type="submit" class="w-full py-3 bg-red-600 text-white font-semibold rounded-lg hover:bg-red-700 transition duration-150 shadow-lg transform hover:scale-[1.01] active:scale-[0.99]">
                🚀 프로그램 등록하기
            </button>
        </form>
    </div>
    
    <script type="module">
        import {{ initializeApp }} from "https://www.gstatic.com/firebasejs/11.6.1/firebase-app.js";
        import {{ getAuth, signInAnonymously, signInWithCustomToken }} from "https://www.gstatic.com/firebasejs/11.6.1/firebase-auth.js";
        import {{ getFirestore, setLogLevel, collection, addDoc }} from "https://www.gstatic.com/firebasejs/11.6.1/firebase-firestore.js";
        
        // --- Global Variables ---
        let db;
        let auth;
        let userId; 
        let appId;
        let isFirebaseReady = false; 
        
        let Regions = {regions_json};
        let Fields = {fields_json};

        let selectedFields = [];
        
        // --- Firebase Initialization ---
        async function initializeFirebase() {{
            try {{
                appId = typeof __app_id !== 'undefined' ? __app_id : 'default-app-id';
                const firebaseConfig = JSON.parse(typeof __firebase_config !== 'undefined' ? __firebase_config : '{{}}');
                const initialAuthToken = typeof __initial_auth_token !== 'undefined' ? __initial_auth_token : null;
                
                const app = initializeApp(firebaseConfig);
                db = getFirestore(app);
                auth = getAuth(app);
                setLogLevel('Debug');
                
                if (initialAuthToken) {{
                    await signInWithCustomToken(auth, initialAuthToken);
                }} else {{
                    await signInAnonymously(auth);
                }}
                
                userId = auth.currentUser?.uid || crypto.randomUUID();
                isFirebaseReady = true; 
                
                setupFormOptions();

            }} catch (error) {{
                console.error("Firebase initialization failed:", error);
                showMessage("Firebase 초기화 중 오류가 발생했습니다.", 'error');
            }}
        }}

        // --- Utility Functions ---
        window.navigate = function(page) {{
            parent.postMessage({{ type: 'NAVIGATE', page: page }}, '*');
        }};
        
        function showMessage(text, type = 'info') {{
            const display = document.getElementById('messageDisplay');
            if (!display) return;

            display.textContent = text;
            display.classList.remove('hidden', 'bg-red-100', 'text-red-700', 'bg-green-100', 'text-green-700');
            
            if (type === 'error') {{
                display.classList.add('bg-red-100', 'text-red-700');
            }} else if (type === 'success') {{
                display.classList.add('bg-green-100', 'text-green-700');
            }} else {{
                display.classList.add('bg-gray-100', 'text-gray-700');
            }}
        }}

        // --- Form Setup Functions ---
        function setupFormOptions() {{
            // 지역 옵션 설정
            const regionSelect = document.getElementById('region');
            Regions.filter(r => r !== '전국').forEach(region => {{ // '전국'은 등록 시 제외
                const option = document.createElement('option');
                option.value = region;
                option.textContent = region;
                regionSelect.appendChild(option);
            }});
            
            // 분야 태그 설정
            const tagsContainer = document.getElementById('fieldTagsContainer');
            Fields.forEach(field => {{
                const button = document.createElement('button');
                button.type = 'button';
                button.textContent = field;
                button.className = 'px-3 py-1 rounded-full border text-sm font-medium transition tag-inactive';
                button.setAttribute('data-field', field);
                button.onclick = () => toggleField(field, button);
                tagsContainer.appendChild(button);
            }});
        }}

        function toggleField(field, button) {{
            const index = selectedFields.indexOf(field);
            const activeClass = 'bg-blue-600 text-white border-blue-600 tag-active';
            const inactiveClass = 'bg-white text-gray-700 border-gray-300 tag-inactive';

            if (index > -1) {{
                selectedFields.splice(index, 1);
                button.className = `px-3 py-1 rounded-full border text-sm font-medium transition ${{inactiveClass}}`;
            }} else {{
                selectedFields.push(field);
                button.className = `px-3 py-1 rounded-full border text-sm font-medium transition ${{activeClass}}`;
            }}
        }}

        // --- Submission Logic ---
        window.submitProgram = async function() {{
            if (!isFirebaseReady) {{
                showMessage("시스템 로딩 중입니다. 잠시 후 다시 시도해주세요.", 'error');
                return;
            }}
            if (selectedFields.length === 0) {{
                showMessage("프로그램 관련 분야를 최소 하나 이상 선택해야 합니다.", 'error');
                return;
            }}

            const programData = {{
                title: document.getElementById('title').value.trim(),
                type: document.getElementById('type').value,
                description: document.getElementById('description').value.trim(),
                region: document.getElementById('region').value,
                url: document.getElementById('url').value.trim() || null,
                img: document.getElementById('img').value.trim() || 'https://placehold.co/400x200/cbd5e1/475569?text=Placeholder',
                fields: selectedFields,
                createdAt: new Date().toISOString(),
                creatorId: userId,
            }};
            
            try {{
                // Firestore에 데이터 추가: /artifacts/{{appId}}/public/data/programs
                const publicDataPath = `/artifacts/${{appId}}/public/data/programs`;
                const programsCollection = collection(db, publicDataPath);
                
                await addDoc(programsCollection, programData);
                
                showMessage("✅ 새 프로그램이 성공적으로 등록되었습니다!", 'success');
                document.getElementById('programForm').reset();
                selectedFields = [];
                setupFormOptions(); // 폼 초기화 후 태그 상태도 초기화
                
            }} catch (e) {{
                console.error("Firestore submission failed:", e);
                showMessage("프로그램 등록 중 오류가 발생했습니다: " + e.message, 'error');
            }}
        }}

        window.onload = initializeFirebase;
    </script>
</body>
</html>
"""
    # JS 중괄호를 이중 중괄호로 이스케이프하여 Python 포맷팅 충돌 회피
    # 단, JSON 데이터는 이스케이프하지 않도록 주의합니다.
    json_regions = json.dumps(REGIONS)
    json_fields = json.dumps(FIELDS)
    
    # 템플릿의 JSON Placeholder를 실제 데이터로 채우고, 
    # 나머지 HTML 콘텐츠는 이스케이프 처리하여 반환합니다.
    final_html = html.replace('{regions_json}', json_regions) \
                     .replace('{fields_json}', json_fields)
    
    return final_html.replace('{', '{{').replace('}', '}}')



# --- 5. Streamlit 페이지 렌더링 함수 (Login) ---
def render_login_page():
    
    login_html_content = get_base64_decoder_html()

    component_value = components.html(
        login_html_content,
        height=600, 
        scrolling=True, 
        key="login_component" # 복구된 key 인수 유지
    )

    if component_value and isinstance(component_value, dict) and component_value.get('type') == 'LOGIN':
        st.session_state['user_authenticated'] = True
        st.session_state['is_admin'] = component_value.get('isAdmin', False)
        st.session_state['current_page'] = 'home'
        st.rerun()

# --- 6. Streamlit 페이지 렌더링 함수 (Home) ---
def render_home_page():
    
    is_admin = st.session_state.get('is_admin', False)

    # 1. BASE HTML 초기화 및 관리자 여부에 따른 템플릿 재생성
    # 관리자 여부에 따라 Home 페이지 템플릿이 달라지므로, 항상 다시 생성합니다.
    base_html_template_unsafe = get_base_home_html_content(is_admin)
    
    # 2. current_html 초기화 및 유효성 검사
    current_content = st.session_state.get('current_home_html')
    
    # 데이터 요청을 위한 초기 HTML 생성
    if not isinstance(current_content, str) or not current_content:
        # 이스케이프된 템플릿에 빈 스크립트를 삽입
        initial_html = base_html_template_unsafe.replace(PAGE_SCRIPT_PLACEHOLDER.replace('{', '{{').replace('}', '}}'), "")
        st.session_state['current_home_html'] = initial_html
        current_content = initial_html

    # 3. HTML 컴포넌트 렌더링
    component_value = components.html(
        current_content, 
        height=1200, 
        scrolling=True,
        key="home_filter_component" # 복구된 key 인수 유지
    )

    # 4. HTML 컴포넌트의 메시지 처리 (데이터 요청 수신, 로그아웃, 페이지 이동)
    if component_value and isinstance(component_value, dict):
        message = component_value

        if message.get('type') == 'GET_INITIAL_DATA':
            
            # HTML로 보낼 데이터 구조
            data_to_send = {
                "type": "PROGRAM_DATA",
                "programs": MOCK_PROGRAMS,
                "regions": REGIONS,
                "fields": FIELDS
            }
            
            # 5. 데이터 전송을 위한 동적 스크립트 생성
            data_json = json.dumps(data_to_send)
            
            # Streamlit에 메시지를 포스트하는 스크립트
            streamlit_data_script = f"""
            <script>
                const dataPayload = {data_json};
                window.postMessage(dataPayload, '*'); 
            </script>
            """
            # 스크립트 내부 중괄호 이스케이프
            streamlit_data_script = streamlit_data_script.replace('{', '{{').replace('}', '}}')

            # 6. 기본 HTML 템플릿에 동적 스크립트를 삽입하여 새로운 HTML 생성
            new_html = base_html_template_unsafe.replace(PAGE_SCRIPT_PLACEHOLDER.replace('{', '{{').replace('}', '}}'), streamlit_data_script)
            
            # 7. 세션 상태 업데이트 및 재실행 요청
            st.session_state['current_home_html'] = new_html
            st.rerun()

        elif message.get('type') == 'LOGOUT':
            st.session_state['user_authenticated'] = False
            st.session_state['current_page'] = 'login'
            if 'current_home_html' in st.session_state:
                del st.session_state['current_home_html']
            st.rerun()
            
        elif message.get('type') == 'NAVIGATE':
            st.session_state['current_page'] = message.get('page')
            st.rerun()

# --- 7. Streamlit 페이지 렌더링 함수 (Admin Add Program) ---
def render_admin_add_program_page():
    
    # 관리자가 아니면 홈으로 돌려보냄
    if not st.session_state.get('is_admin'):
        st.session_state['current_page'] = 'home'
        st.warning("관리자 권한이 없습니다.")
        st.rerun()
        return

    st.title("관리자: 새 진로 프로그램 추가")
    
    admin_html_content = get_admin_add_program_html_content()

    component_value = components.html(
        admin_html_content, 
        height=1000, 
        scrolling=True,
        key="admin_add_program_component" # 복구된 key 인수 유지
    )
    
    # HTML 컴포넌트의 메시지 처리 (페이지 이동)
    if component_value and isinstance(component_value, dict):
        if component_value.get('type') == 'NAVIGATE':
            st.session_state['current_page'] = component_value.get('page')
            st.rerun()


# --- 8. 메인 실행 블록 ---
if __name__ == '__main__':
    st.set_page_config(layout="wide")

    # 인증 및 페이지 상태 설정
    if 'user_authenticated' not in st.session_state:
        st.session_state['user_authenticated'] = False 
        st.session_state['is_admin'] = False
        st.session_state['current_page'] = 'login'

    # 현재 페이지 상태에 따라 라우팅
    if not st.session_state.get('user_authenticated'):
        render_login_page()
    elif st.session_state.get('current_page') == 'home':
        st.subheader(f"환영합니다! ({'관리자' if st.session_state.get('is_admin') else '일반 사용자'})")
        render_home_page()
    elif st.session_state.get('current_page') == 'admin_add':
        render_admin_add_program_page()
    else:
        # 정의되지 않은 페이지는 홈으로 리다이렉션
        st.session_state['current_page'] = 'home'
        st.rerun()
