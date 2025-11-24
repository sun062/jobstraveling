import streamlit as st
import streamlit.components.v1 as components
import json

# --- 0. 이스케이프 유틸리티 함수 (KeyError 방지) ---
def escape_curly_braces(html_content):
    """
    KeyError를 방지하기 위해 포맷팅 키가 아닌 모든 중괄호({, })를 {{, }}로 이스케이프 처리합니다.
    {streamlit_data_script} 키만 이스케이프하지 않도록 특별히 처리합니다.
    """
    # 1. 포맷팅 키를 임시 Placeholder로 대체
    placeholder = "__STREAMLIT_SCRIPT_PLACEHOLDER__"
    content = html_content.replace("{streamlit_data_script}", placeholder)
    
    # 2. 모든 일반 중괄호 이스케이프 처리
    content = content.replace("{", "{{").replace("}", "}}")
    
    # 3. Placeholder를 포맷팅 키로 다시 복원
    return content.replace(placeholder, "{streamlit_data_script}")


# --- 1. Mock 데이터 정의 (실제로는 DB 또는 API에서 가져와야 합니다) ---
MOCK_PROGRAMS = [
    {"id": 1, "title": "서울시 IT 미래 인재 캠프", "region": "서울", "type": "진로", "url": "https://www.google.com/search?q=서울시+IT+캠프", "img": "https://placehold.co/400x200/4f46e5/ffffff?text=IT+Camp", "description": "IT 기술 체험 및 현직자 멘토링 프로그램.", "fields": ["AI/IT", "과학/기술"]},
    {"id": 2, "title": "부산항만 공사 견학", "region": "부산", "type": "견학", "url": "https://www.google.com/search?q=부산항만+견학", "img": "https://placehold.co/400x200/059669/ffffff?text=Port+Tour", "description": "대한민국 최대 항만의 물류 흐름 체험.", "fields": ["운송/물류", "사회/인문"]},
    {"id": 3, "title": "경기 AI 로봇 체험관", "region": "경기", "type": "진로", "url": "https://www.google.com/search?q=경기+AI+로봇", "img": "https://placehold.co/400x200/f59e0b/ffffff?text=AI+Robot", "description": "첨단 로봇 기술을 직접 만져보고 체험하는 기회.", "fields": ["AI/IT", "과학/기술", "기계/제조"]},
    {"id": 4, "title": "광주 자동차 미래 산업 탐방", "region": "광주", "type": "견학", "url": "https://www.google.com/search?q=광주+자동차+탐방", "img": "https://placehold.co/400x200/dc2626/ffffff?text=Car+Industry", "description": "친환경 자동차 생산 라인 및 연구소 방문.", "fields": ["기계/제조", "과학/기술"]},
    {"id": 5, "title": "강원 환경보호 교육 캠페인", "region": "강원", "type": "진로", "url": "https://www.google.com/search?q=강원+환경+캠페인", "img": "https://placehold.co/400x200/10b981/ffffff?text=Eco+Camp", "description": "지속 가능한 환경과 관련된 직업군 탐색.", "fields": ["생명/환경", "사회/인문"]},
    {"id": 6, "title": "서울 고궁 문화 해설사 체험", "region": "서울", "type": "진로", "url": "https://www.google.com/search?q=서울+문화+해설사", "img": "https://placehold.co/400x200/5a32a8/ffffff?text=Culture+Guide", "description": "역사 해설 및 문화재 보존 체험.", "fields": ["예술/문화", "사회/인문"]},
    {"id": 7, "title": "대전 나노 반도체 특강", "region": "대전", "type": "진로", "url": "https://www.google.com/search?q=대전+반도체+특강", "img": "https://placehold.co/400x200/3498db/ffffff?text=Semiconductor", "description": "미래 기술의 핵심, 반도체 제조 과정 이해.", "fields": ["과학/기술", "AI/IT", "화학"]},
]

REGIONS = ["전국", "서울", "부산", "대구", "인천", "광주", "대전", "울산", "세종", "경기", "강원", "충북", "충남", "전북", "전남", "경북", "경남", "제주"]
FIELDS = ["AI/IT", "생명/환경", "화학", "문학/언론", "예술/문화", "교육/보건", "금융/경제", "기계/제조", "운송/물류", "사회/인문", "과학/기술"]

# --- 2. HTML 콘텐츠 (기본 템플릿) 로드 ---
def get_base_html_content():
    """Streamlit 세션 상태에 저장할 기본 HTML 템플릿을 반환합니다. {streamlit_data_script}를 포함합니다."""
    html = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>잡스트레블링 - 홈</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body { 
            font-family: 'Inter', sans-serif; 
            background-color: #f0f4f8; 
            min-height: 100vh; 
            margin: 0;
            padding: 0;
        }
        .header-bg {
            background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
        }
        .program-card {
            transition: transform 0.2s, box-shadow 0.2s;
        }
        .program-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
        }
        .tag-active {
            background-color: #2563eb; /* Blue 700 */
            color: white;
            border-color: #2563eb;
        }
        .tag-inactive {
            background-color: #e0f2f7; /* Light Cyan */
            color: #0c4a6e; /* Cyan 900 */
            border-color: #bae6fd; /* Cyan 200 */
        }
    </style>
</head>
<body class="p-0">

    <!-- 1. 상단 헤더 및 검색 바 -->
    <header class="header-bg p-4 shadow-lg sticky top-0 z-10">
        <div class="max-w-4xl mx-auto flex justify-between items-center text-white">
            <h1 class="text-2xl font-bold">🗺️ Job-Trekking 홈</h1>
            <button onclick="requestStreamlitLogout()" class="text-sm px-3 py-1 bg-white bg-opacity-20 rounded-full hover:bg-opacity:30 transition">
                로그아웃
            </button>
        </div>
        
        <!-- 선택형 검색 입력 영역 -->
        <div class="max-w-4xl mx-auto mt-4 grid grid-cols-2 gap-3">
            
            <!-- 지역 선택 박스 -->
            <div id="regionSelectBox" onclick="showRegionModal()" 
                 class="p-3 bg-white rounded-xl shadow-md text-gray-800 cursor-pointer flex items-center justify-between transition hover:ring-2 hover:ring-blue-300">
                <span id="selectedRegionText" class="truncate font-medium text-gray-600">지역 선택 (필수)</span>
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                </svg>
            </div>

            <!-- 분야 선택 박스 -->
            <div id="fieldSelectBox" onclick="showFieldModal()" 
                 class="p-3 bg-white rounded-xl shadow-md text-gray-800 cursor-pointer flex items-center justify-between transition hover:ring-2 hover:ring-blue-300">
                <span id="selectedFieldText" class="truncate font-medium text-gray-600">분야 선택 (다중 선택 가능)</span>
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                </svg>
            </div>
        </div>

        <!-- 현재 검색 조건 표시 및 초기화 버튼 -->
        <div class="max-w-4xl mx-auto mt-3 flex justify-between items-center">
             <div id="currentFilters" class="text-sm text-white font-light">
                 <!-- 선택된 필터가 여기에 표시됩니다. -->
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

    <!-- 3. Footer (선택 사항) -->
    <footer class="text-center text-gray-500 text-sm py-6 border-t mt-10">
        © 2024 Job-Trekking | 모든 프로그램 정보는 주관사에 귀속됩니다.
    </footer>
    
    <!-- 메시지 박스 (Firebase Error / Logout Confirm) -->
    <div id="messageBox" class="hidden fixed inset-0 bg-gray-600 bg-opacity-50 z-50 flex items-center justify-center p-4">
        <div class="bg-white p-6 rounded-xl shadow-xl max-w-sm w-full text-center">
            <p id="messageText" class="text-gray-800 font-medium mb-4"></p>
            <button onclick="continueAction()" class="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition">확인</button>
        </div>
    </div>

    <!-- 지역 선택 모달 -->
    <div id="regionModal" class="hidden fixed inset-0 bg-gray-600 bg-opacity-75 z-50 flex items-center justify-center p-4">
        <div class="bg-white p-6 rounded-xl shadow-2xl max-w-lg w-full">
            <h3 class="text-lg font-bold mb-4 border-b pb-2">지역 선택 (시/도)</h3>
            <div id="regionOptions" class="grid grid-cols-3 sm:grid-cols-4 gap-3 max-h-80 overflow-y-auto">
                <!-- 지역 버튼들이 여기에 생성됩니다. -->
            </div>
            <button onclick="hideRegionModal()" class="mt-6 w-full px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition">닫기</button>
        </div>
    </div>

    <!-- 분야 선택 모달 (다중 선택) -->
    <div id="fieldModal" class="hidden fixed inset-0 bg-gray-600 bg-opacity-75 z-50 flex items-center justify-center p-4">
        <div class="bg-white p-6 rounded-xl shadow-2xl max-w-lg w-full">
            <h3 class="text-lg font-bold mb-4 border-b pb-2">분야 선택 (다중 선택)</h3>
            <div id="fieldOptions" class="flex flex-wrap gap-2 max-h-80 overflow-y-auto">
                <!-- 분야 태그들이 여기에 생성됩니다. -->
            </div>
            <button onclick="applyFieldSelection()" class="mt-6 w-full px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition">선택 완료</button>
        </div>
    </div>

    <script type="module">
        // Firebase 초기화 및 인증 로직
        import { initializeApp } from "https://www.gstatic.com/firebasejs/11.6.1/firebase-app.js";
        import { getAuth, signInAnonymously, signInWithCustomToken } from "https://www.gstatic.com/firebasejs/11.6.1/firebase-auth.js";
        import { getFirestore, setLogLevel } from "https://www.gstatic.com/firebasejs/11.6.1/firebase-firestore.js";
        
        let db;
        let auth;
        let userId; 
        let appId;
        let isFirebaseReady = false; 
        
        // --- 데이터 변수 (백엔드에서 수신) ---
        let Programs = []; 
        let Regions = []; 
        let Fields = []; 

        // --- 상태 관리 변수 ---
        let currentRegion = ""; 
        let currentFields = []; 
        
        // --- Firebase 초기화 함수 ---
        async function initializeFirebase() {
            try {
                appId = typeof __app_id !== 'undefined' ? __app_id : 'default-app-id';
                const firebaseConfig = JSON.parse(typeof __firebase_config !== 'undefined' ? __firebase_config : '{}');
                // __initial_auth_token이 'undefined'가 아닐 때만 사용
                const initialAuthToken = typeof __initial_auth_token !== 'undefined' ? __initial_auth_token : null;
                
                const app = initializeApp(firebaseConfig);
                db = getFirestore(app);
                auth = getAuth(app);
                setLogLevel('Debug');
                
                if (initialAuthToken) {
                    await signInWithCustomToken(auth, initialAuthToken);
                } else {
                    await signInAnonymously(auth);
                }
                
                userId = auth.currentUser?.uid || crypto.randomUUID();
                isFirebaseReady = true; 
                console.log("Firebase initialized successfully. User ID:", userId);
                
                if (typeof onPageLoad === 'function') {
                    onPageLoad(); 
                }

            } catch (error) {
                console.error("Firebase initialization or sign-in failed:", error);
                showMessage("Firebase 초기화 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.");
            }
        }
        
        // --- 유틸리티 함수 (메시지 박스) ---
        let globalNextAction = null;
        function showMessage(text, action = null) {
            const messageBox = document.getElementById('messageBox');
            const messageText = document.getElementById('messageText');
            
            messageText.textContent = text;
            globalNextAction = action; 
            if (messageBox) messageBox.classList.remove('hidden');
        }

        function hideMessage() {
            const messageBox = document.getElementById('messageBox');
            if (messageBox) messageBox.classList.add('hidden');
        }
        
        window.continueAction = function() { // 전역 함수로 등록
            hideMessage();
            if (typeof globalNextAction === 'function') {
                globalNextAction(); 
                globalNextAction = null; 
            }
        }

        // --- 백엔드 (app.py) 통신 관련 함수 ---
        
        // Streamlit에 초기 데이터 요청
        function requestInitialData() {
            parent.postMessage({ type: 'GET_INITIAL_DATA' }, '*');
        }

        // Streamlit에 로그아웃 요청
        function requestStreamlitLogout() {
             showMessage('로그아웃 하시겠습니까?', () => {
                 parent.postMessage({type: 'NAVIGATE', page: 'login'}, '*');
             });
        }
        
        // 백엔드에서 메시지를 수신하는 리스너
        window.addEventListener('message', (event) => {
            if (event.source !== window.parent) return;

            const data = event.data;
            if (typeof data !== 'object' || data === null) return;

            switch (data.type) {
                case 'PROGRAM_DATA':
                    Programs = data.programs || [];
                    Regions = data.regions || [];
                    Fields = data.fields || [];
                    
                    createRegionOptions();
                    createFieldOptions();
                    filterPrograms();
                    break;
                case 'ERROR_MESSAGE':
                    showMessage(data.message || '알 수 없는 오류가 발생했습니다.');
                    break;
                default:
                    break;
            }
        });
        
        window.onload = initializeFirebase;
        
        // --- 프로그램 렌더링 및 필터링 로직 ---
        
        function createProgramCard(program) {
            const card = document.createElement('a');
            card.href = program.url; 
            card.target = "_blank"; 
            card.className = "program-card bg-white rounded-xl shadow-lg overflow-hidden cursor-pointer block border border-gray-100 hover:border-blue-300";
            
            const typeColor = program.type === '진로' ? 'bg-indigo-100 text-indigo-700' : 'bg-green-100 text-green-700';

            const fieldTags = (program.fields || []).map(field => 
                `<span class="text-xs font-light px-2 py-0.5 rounded-full bg-gray-100 text-gray-600">{{field}}</span>`
            ).join('');

            card.innerHTML = `
                <img src="${program.img}" onerror="this.onerror=null; this.src='https://placehold.co/400x200/cbd5e1/475569?text=Image+Not+Found';" alt="${program.title}" class="w-full h-40 object-cover">
                <div class="p-4 space-y-2">
                    <div class="flex items-center space-x-2">
                        <span class="text-xs font-semibold px-2 py-0.5 rounded-full ${typeColor}">${program.type}</span>
                        ${fieldTags}
                    </div>
                    <h3 class="text-lg font-bold text-gray-800 truncate">${program.title}</h3>
                    <p class="text-sm text-gray-500">${program.description}</p>
                    <p class="text-xs text-gray-400 font-medium flex items-center">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.828 0l-4.243-4.243a8 8 0 1111.314 0z" /><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" /></svg>
                        ${program.region}
                    </p>
                </div>
            `;

            return card;
        }

        function renderPrograms(programs) {
            const container = document.getElementById('programList');
            if (!container) return;

            container.innerHTML = '';
            
            if (programs.length === 0) {
                container.innerHTML = '<p class="col-span-full text-center text-gray-500 py-10">현재 조건에 맞는 프로그램이 없습니다. 검색 조건을 변경해 보세요.</p>';
                return;
            }

            programs.forEach(program => {
                container.appendChild(createProgramCard(program));
            });
        }
        
        window.filterPrograms = function() {
            const regionToFilter = currentRegion === "전국" || currentRegion === "" ? null : currentRegion;
            const fieldsToFilter = currentFields.length > 0 ? currentFields : null;

            const filtered = Programs.filter(program => {
                const regionMatch = !regionToFilter || program.region === regionToFilter;
                const fieldMatch = !fieldsToFilter || fieldsToFilter.some(field => (program.fields || []).includes(field));

                return regionMatch && fieldMatch;
            });

            renderPrograms(filtered);
            updateFilterDisplay();
        }

        function updateFilterDisplay() {
            const regionText = currentRegion || "전국";
            const fieldText = currentFields.length > 0 ? currentFields.length + "개 분야 선택됨" : "전체 분야";
            
            document.getElementById('selectedRegionText').textContent = currentRegion || "지역 선택 (필수)";
            document.getElementById('selectedFieldText').textContent = fieldText;
            
            document.getElementById('currentFilters').innerHTML = `
                현재 필터: <span class="font-bold">${regionText}</span> & <span class="font-bold">${fieldText}</span>
            `;
        }

        window.resetFilters = function() {
            currentRegion = "";
            currentFields = [];
            filterPrograms();
            showMessage('검색 조건이 초기화되었습니다.');
        }

        window.onPageLoad = function() {
            requestInitialData();
            updateFilterDisplay();
        }
        
        // --- 모달 관련 로직 ---

        function createRegionOptions() {
            const container = document.getElementById('regionOptions');
            container.innerHTML = ''; 
            Regions.forEach(region => {
                const button = document.createElement('button');
                button.textContent = region;
                button.className = "p-2 rounded-lg border border-gray-300 bg-white hover:bg-blue-500 hover:text-white transition text-sm font-medium";
                button.onclick = () => selectRegion(region);
                container.appendChild(button);
            });
        }

        function selectRegion(region) {
            currentRegion = region;
            hideRegionModal();
            filterPrograms(); 
            updateFilterDisplay();
        }

        window.showRegionModal = function() {
            if (!isFirebaseReady || Regions.length === 0) {
                 showMessage('데이터를 로딩 중이거나 Firebase 초기화 중입니다. 잠시 후 다시 시도해주세요.');
                 return;
            }
            document.getElementById('regionModal').classList.remove('hidden');
        }

        window.hideRegionModal = function() {
            document.getElementById('regionModal').classList.add('hidden');
        }

        function createFieldOptions() {
            const container = document.getElementById('fieldOptions');
            container.innerHTML = ''; 
            Fields.forEach(field => {
                const button = document.createElement('button');
                button.textContent = field;
                button.setAttribute('data-field', field);
                
                const isActive = currentFields.includes(field);
                button.className = `px-3 py-1 rounded-full border text-sm font-medium transition ${isActive ? 'tag-active' : 'tag-inactive'}`;
                
                button.onclick = () => toggleField(field, button);
                container.appendChild(button);
            });
        }
        
        function toggleField(field, button) {
            const index = currentFields.indexOf(field);
            if (index > -1) {
                currentFields.splice(index, 1);
                button.classList.remove('tag-active');
                button.classList.add('tag-inactive');
            } else {
                currentFields.push(field);
                button.classList.remove('tag-inactive');
                button.classList.add('tag-active');
            }
        }
        
        window.showFieldModal = function() {
            if (!isFirebaseReady || Fields.length === 0) {
                 showMessage('데이터를 로딩 중이거나 Firebase 초기화 중입니다. 잠시 후 다시 시도해주세요.');
                 return;
            }
            // 모달을 열 때 현재 상태를 반영합니다.
            document.querySelectorAll('#fieldOptions button').forEach(button => {
                const field = button.getAttribute('data-field');
                const isActive = currentFields.includes(field);
                button.classList.toggle('tag-active', isActive);
                button.classList.toggle('tag-inactive', !isActive);
            });
            document.getElementById('fieldModal').classList.remove('hidden');
        }

        window.applyFieldSelection = function() {
            document.getElementById('fieldModal').classList.add('hidden');
            filterPrograms();
            updateFilterDisplay();
        }
        
        updateFilterDisplay();

    </script>
    {streamlit_data_script}
</body>
</html>
"""
    return escape_curly_braces(html)

# --- 3. Streamlit 페이지 렌더링 함수 ---
def render_home_page():
    
    # 1. BASE HTML 초기화 (1회만 실행)
    if 'base_html' not in st.session_state:
        st.session_state['base_html'] = get_base_html_content()
        
    # **수정된 부분: current_html을 안전하게 추출하고, 없거나 문자열이 아니면 기본값으로 강제 초기화합니다.**
    # 기본 HTML 템플릿 (빈 스크립트 포함)
    default_html = st.session_state.get('base_html', "<h1>Error: HTML template missing.</h1>").format(streamlit_data_script="")
    
    # 현재 콘텐츠를 안전하게 가져옵니다.
    current_content = st.session_state.get('current_html')
    
    # current_content가 없거나 문자열이 아니면 기본값으로 재설정
    if not isinstance(current_content, str):
        current_content = default_html
        st.session_state['current_html'] = current_content # 세션 상태에도 반영

    # 3. HTML 컴포넌트 렌더링
    # current_content는 이제 유효한 문자열임이 보장됩니다.
    component_value = components.html(
        current_content,
        height=1200, 
        scrolling=True,
        key="home_filter_component"
    )

    # 4. HTML 컴포넌트의 메시지 처리 (데이터 요청 수신)
    if component_value:
        message = component_value

        if isinstance(message, dict) and message.get('type') == 'GET_INITIAL_DATA':
            
            # HTML로 보낼 데이터 구조
            data_to_send = {
                "type": "PROGRAM_DATA",
                "programs": MOCK_PROGRAMS,
                "regions": REGIONS,
                "fields": FIELDS
            }
            
            # 5. 데이터 전송을 위한 동적 스크립트 생성
            data_json = json.dumps(data_to_send)
            
            streamlit_data_script = f"""
            <script>
                // 데이터 주입 스크립트: Streamlit Python 백엔드에서 받은 데이터를 JS로 주입
                const dataPayload = {data_json};
                // 스크립트 로드 즉시 데이터를 전송하여 JavaScript가 처리하도록 합니다.
                window.parent.postMessage(dataPayload, '*'); 
            </script>
            """
            
            # 6. 기본 HTML 템플릿에 동적 스크립트를 삽입하여 새로운 HTML 생성
            new_html = st.session_state['base_html'].format(streamlit_data_script=streamlit_data_script)
            
            # 7. 세션 상태 업데이트 및 재실행 요청
            st.session_state['current_html'] = new_html
            st.rerun()

# --- 4. 메인 실행 블록 ---
if __name__ == '__main__':
    st.set_page_config(layout="wide")

    # 가짜 인증 세션 상태 설정
    if 'user_authenticated' not in st.session_state:
        st.session_state['user_authenticated'] = True 

    if st.session_state.get('user_authenticated'):
        st.title("잡스트레블링 - 홈 (Streamlit)")
        render_home_page()
    else:
        st.error("로그인 페이지로 이동해야 합니다.")
