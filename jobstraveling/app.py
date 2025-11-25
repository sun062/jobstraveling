import streamlit as st
import streamlit.components.v1 as components
import os
import json
from datetime import date, datetime
import time # 지연 처리를 위해 time 모듈 추가

# --- Firebase SDK Admin (Python) 사용을 위한 Stubs ---
# Python에서 Firestore에 접근하기 위해 가상의 함수를 정의합니다.
# 실제 Firebase Admin SDK를 가져올 수 없으므로, on-premise 환경에서는
# 이 부분이 실제 데이터베이스 접근 로직으로 대체됩니다.
# 이 환경에서는 Streamlit이 백엔드 역할을 하므로, `st.session_state`에
# 임시 데이터베이스 스텁을 만들어 사용하겠습니다.
if 'firestore_reports' not in st.session_state:
    st.session_state.firestore_reports = {} # {userId: [report1, report2, ...]}
if 'firestore_programs' not in st.session_state:
    # 프로그램 목록 초기 데이터 (Mock Program Data)
    st.session_state.firestore_programs = [
        {'id': '1', 'name': 'AI 개발자 체험 프로그램', 'field': 'IT/소프트웨어', 'description': '인공지능 모델을 직접 설계하고 코딩하는 경험', 'date': '2024-11-20', 'location': '온라인'},
        {'id': '2', 'name': '친환경 건축가 워크숍', 'field': '건설/환경', 'description': '지속 가능한 건축 설계 및 재료 탐구', 'date': '2024-12-05', 'location': '서울 건축센터'},
        {'id': '3', 'name': '우주 과학자 진로 특강', 'field': '과학/연구', 'description': 'NASA 탐사선 데이터 분석 및 우주 관측', 'date': '2025-01-10', 'location': '대학 강당'},
    ]


# --- Global Environment Variables ---
# Canvas 환경 변수 로드 (Firestore 사용을 위한 필수 변수)
firebaseConfig = json.loads(os.environ.get('__firebase_config', '{}'))
appId = os.environ.get('__app_id', 'default-app-id')
initialAuthToken = os.environ.get('__initial_auth_token', '')

# --- 1. 환경 설정 및 세션 상태 초기화 ---
st.set_page_config(layout="centered", initial_sidebar_state="expanded")

# 페이지 정의 상수
PAGE_LOGIN = 'login'
PAGE_SIGNUP = 'signup'
PAGE_HOME = 'home'
PAGE_PROGRAM_LIST = 'program_list'
PAGE_ADD_PROGRAM = 'add_program'
PAGE_ADD_REPORT = 'add_report'      # 잡스리포트 기록 페이지
PAGE_VIEW_REPORTS = 'view_reports' # 잡스리포트 목록/상세 보기 페이지

# 세션 상태 초기화
if 'current_page' not in st.session_state:
    st.session_state.current_page = PAGE_LOGIN
if 'user_data' not in st.session_state:
    st.session_state.user_data = None # 로그인한 사용자 정보
if 'is_auth_ready' not in st.session_state:
    st.session_state.is_auth_ready = False
if 'mock_user' not in st.session_state:
    # 기본 Mock 사용자 정보 설정 (관리자 계정)
    st.session_state.mock_user = {
        'email': 'admin@jobtrekking.com', 
        'password': 'adminpassword',
        'schoolName': '관리자 학교',
        'classNumber': '999',
        'studentName': '관리자',
        'birthDate': '2000-01-01',
        'isAdmin': True 
    }
# 일반 사용자 Mock 계정 
if 'mock_user_normal' not in st.session_state:
    st.session_state.mock_user_normal = {
        'email': 'user@jobtrekking.com', 
        'password': 'userpassword',
        'schoolName': '일반 고등학교',
        'classNumber': '101',
        'studentName': '일반사용자',
        'birthDate': '2007-01-01',
        'isAdmin': False
    }

# 리포트 폼 데이터를 저장할 세션 상태 (HTML 컴포넌트에서 전달받음)
if 'current_report_data' not in st.session_state:
    st.session_state.current_report_data = None
if 'report_saved_successfully' not in st.session_state:
    st.session_state.report_saved_successfully = False

# --- Firebase Stubs (Python Backend) ---

def get_current_user_id():
    """Mock User ID 반환. 실제 환경에서는 __initial_auth_token을 파싱해야 합니다."""
    # 간단히 Mock 사용자 이메일을 ID로 사용합니다.
    return st.session_state.user_data.get('email') if st.session_state.user_data else None

def save_report_to_firestore(report_data):
    """
    Python 백엔드에서 리포트 데이터를 저장합니다.
    실제 Firestore SDK 없이 세션 상태를 임시 저장소로 사용합니다.
    """
    user_id = get_current_user_id()
    if not user_id:
        return False, "사용자 인증 정보를 찾을 수 없습니다."

    # 필수 필드 유효성 검사 (Streamlit 버튼에서 이미 체크하지만, 백엔드에서도 최종 확인)
    if not report_data or not report_data.get('programName') or not report_data.get('experienceDate') or report_data.get('rating') is None or not report_data.get('reportContent'):
        return False, "체험 프로그램명, 일자, 별점, 소감 내용을 모두 입력해 주세요."
    
    # Firestore Data Structure Stub
    if user_id not in st.session_state.firestore_reports:
        st.session_state.firestore_reports[user_id] = []
    
    # 날짜 문자열을 Date 객체로 변환하여 저장
    
    report_data['id'] = str(len(st.session_state.firestore_reports[user_id]) + 1) # 임시 ID 부여
    report_data['createdAt'] = datetime.now().isoformat()
    
    st.session_state.firestore_reports[user_id].append(report_data)
    
    return True, ""


# --- 2. HTML 파일 로드 함수 ---
def read_html_file(file_name):
    """HTML 파일을 읽어 문자열로 반환합니다. (htmls 폴더 내에서 파일을 찾습니다)"""
    # ⭐️ 경로 문제 해결을 위해 현재 스크립트의 절대 경로를 기준으로 파일을 찾습니다.
    # __file__은 현재 실행 중인 파일(app.py)의 경로를 나타냅니다.
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, 'htmls', file_name)
    
    try:
        # 파일을 직접 읽는 대신, 파일이 없다고 가정하고 mock HTML을 반환합니다. 
        # 이는 Canvas 환경의 제약사항을 우회하기 위함입니다.
        if file_name == 'home.html':
            return """
            <style>
                .card {
                    background: white;
                    border-radius: 12px;
                    padding: 20px;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                    margin-bottom: 20px;
                }
                .section-title {
                    font-size: 1.5rem;
                    color: #1e40af;
                    border-bottom: 2px solid #bfdbfe;
                    padding-bottom: 5px;
                    margin-bottom: 15px;
                }
            </style>
            <div class="card">
                <h2 class="section-title">👤 사용자 정보</h2>
                <p><strong>이름:</strong> {{USER_NAME}}</p>
                <p><strong>학교:</strong> {{USER_SCHOOL}}</p>
                <p><strong>반 번호:</strong> {{USER_CLASS}}</p>
                <p><strong>권한:</strong> {{USER_IS_ADMIN}}</p>
            </div>
            <div class="card">
                <h2 class="section-title">📊 나의 활동 요약</h2>
                <p>총 기록된 리포트 수: <span id="reportCount">0</span>개</p>
                <p>가장 최근 기록일: <span id="lastReportDate">없음</span></p>
            </div>
            <div class="card">
                <h2 class="section-title">🎯 이번 주 추천 진로 분야</h2>
                <ul style="list-style-type: none; padding: 0;">
                    <li style="padding: 5px 0; border-bottom: 1px dashed #eee;">⭐ AI와 데이터 사이언스</li>
                    <li style="padding: 5px 0; border-bottom: 1px dashed #eee;">⭐ 친환경 에너지 기술</li>
                    <li style="padding: 5px 0;">⭐ 미디어 콘텐츠 기획</li>
                </ul>
            </div>
            """
        elif file_name == 'program_list.html':
            return """
            <script src="https://www.gstatic.com/firebasejs/11.6.1/firebase-app.js"></script>
            <script src="https://www.gstatic.com/firebasejs/11.6.1/firebase-auth.js"></script>
            <script src="https://www.gstatic.com/firebasejs/11.6.1/firebase-firestore.js"></script>
            
            <div id="program-list-app" style="font-family: Arial, sans-serif;">
                <h2 style="color: #1e40af;">등록된 프로그램 목록 (Mock Data)</h2>
                <p style="color: #6b7280;">현재 Streamlit 세션에 저장된 Mock 프로그램 목록을 표시합니다. (실제 Firestore 연동 아님)</p>
                <div id="program-container">
                    <ul style="list-style-type: none; padding: 0;" id="program-list">
                        <!-- 프로그램 목록이 여기에 로드됩니다 -->
                        <li style="padding: 15px; border: 1px solid #ddd; border-radius: 8px; margin-bottom: 10px; background-color: #f9f9f9;">
                            <strong style="color: #333;">AI 개발자 체험 프로그램</strong> (IT/소프트웨어) - 2024-11-20
                        </li>
                        <li style="padding: 15px; border: 1px solid #ddd; border-radius: 8px; margin-bottom: 10px; background-color: #f9f9f9;">
                            <strong style="color: #333;">친환경 건축가 워크숍</strong> (건설/환경) - 2024-12-05
                        </li>
                        <li style="padding: 15px; border: 1px solid #ddd; border-radius: 8px; margin-bottom: 10px; background-color: #f9f9f9;">
                            <strong style="color: #333;">우주 과학자 진로 특강</strong> (과학/연구) - 2025-01-10
                        </li>
                    </ul>
                </div>
            </div>
            """
        elif file_name == 'add_program.html':
            return """
            <h2 style="color: #ef4444;">새 프로그램 추가 기능 (Mock)</h2>
            <p>관리자님, 프로그램을 추가하는 기능은 현재 Python 백엔드의 Mock 리스트에만 임시로 저장됩니다.</p>
            <form id="addProgramForm">
                <label for="programName">프로그램명:</label><br>
                <input type="text" id="programName" name="programName" style="width: 90%; padding: 8px; margin-bottom: 10px; border: 1px solid #ccc; border-radius: 4px;" required><br>
                
                <label for="jobField">관련 분야:</label><br>
                <input type="text" id="jobField" name="jobField" value="IT/소프트웨어" style="width: 90%; padding: 8px; margin-bottom: 10px; border: 1px solid #ccc; border-radius: 4px;" required><br>

                <button type="submit" style="background-color: #ef4444; color: white; padding: 10px 15px; border: none; border-radius: 4px; cursor: pointer;">프로그램 등록 (Mock)</button>
            </form>
            <script>
                document.getElementById('addProgramForm').addEventListener('submit', function(e) {
                    e.preventDefault();
                    alert('프로그램이 Mock 리스트에 추가되었습니다! (실제 Firestore 저장 아님)');
                    // Streamlit과의 통신 없이 단순 알림
                });
            </script>
            """
        elif file_name == 'add_report.html':
            return """
            <style>
                #reportForm label { font-weight: bold; display: block; margin-top: 15px; color: #1e40af;}
                #reportForm input[type="text"], #reportForm input[type="date"], #reportForm select, #reportForm textarea { 
                    width: 100%; padding: 10px; margin-top: 5px; border: 1px solid #ccc; border-radius: 6px; box-sizing: border-box; 
                }
                #rating-stars { font-size: 2rem; cursor: pointer; user-select: none; }
                .star { color: #ccc; transition: color 0.2s; }
                .star.filled { color: #fbbf24; }
                .report-button {
                    background-color: #10b981; color: white; padding: 12px 20px; border: none; border-radius: 8px; 
                    cursor: pointer; font-size: 1.1rem; margin-top: 30px; width: 100%; transition: background-color 0.3s;
                }
                .report-button:hover { background-color: #059669; }
            </style>
            <form id="reportForm">
                <input type="hidden" id="ratingValue" name="rating" value="0">
                
                <label for="programName">체험 프로그램명 (필수)</label>
                <input type="text" id="programName" name="programName" required>

                <label for="experienceDate">체험 일자 (필수)</label>
                <input type="date" id="experienceDate" name="experienceDate" required>
                
                <label for="jobField">관련 진로 분야</label>
                <input type="text" id="jobField" name="jobField" value="미입력">

                <label>체험 만족도 (별점, 필수)</label>
                <div id="rating-stars">
                    <span class="star" data-rating="1">★</span>
                    <span class="star" data-rating="2">★</span>
                    <span class="star" data-rating="3">★</span>
                    <span class="star" data-rating="4">★</span>
                    <span class="star" data-rating="5">★</span>
                </div>

                <label for="reportContent">체험 소감 및 내용 (필수)</label>
                <textarea id="reportContent" name="reportContent" rows="8" required></textarea>

                <button type="submit" class="report-button">📝 잡스리포트 저장</button>
            </form>

            <script>
                const stars = document.querySelectorAll('.star');
                const ratingInput = document.getElementById('ratingValue');
                
                stars.forEach(star => {
                    star.addEventListener('click', (e) => {
                        const rating = parseInt(e.target.dataset.rating);
                        ratingInput.value = rating;
                        updateStars(rating);
                    });
                });

                function updateStars(currentRating) {
                    stars.forEach(star => {
                        const starRating = parseInt(star.dataset.rating);
                        if (starRating <= currentRating) {
                            star.classList.add('filled');
                        } else {
                            star.classList.remove('filled');
                        }
                    });
                }
                
                // 폼 제출 처리
                document.getElementById('reportForm').addEventListener('submit', function(e) {
                    e.preventDefault();
                    
                    const form = e.target;
                    const reportData = {};
                    
                    // 폼 데이터를 객체로 변환
                    new FormData(form).forEach((value, key) => {
                        // rating은 숫자로 변환
                        if (key === 'rating') {
                            reportData[key] = parseInt(value);
                        } else {
                            reportData[key] = value;
                        }
                    });
                    
                    // Streamlit으로 데이터와 제출 플래그를 전송
                    Streamlit.setComponentValue({
                        reportData: reportData,
                        submitted: true
                    });
                });

                // Streamlit 컴포넌트 라이브러리 로드
                (function() {
                    const script = document.createElement('script');
                    script.src = 'https://cdn.jsdelivr.net/gh/streamlit/streamlit-component-lib@1.0.3/dist/streamlit-component-lib.js';
                    script.onload = () => Streamlit.setComponentReady();
                    document.head.appendChild(script);
                })();

                // 초기 별점 설정 (만약 이전 데이터가 있다면)
                updateStars(parseInt(ratingInput.value));
            </script>
            """
        else:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
    except FileNotFoundError:
        st.error(f"⚠️ HTML 파일을 찾을 수 없습니다. 'htmls/{file_name}' 경로를 확인해 주세요.")
        return ""
    except Exception as e:
        st.error(f"파일 읽기 중 예기치 않은 오류 발생: {e}")
        return ""

# --- 3. 페이지 전환 ---
def navigate(page):
    """세션 상태를 변경하여 페이지를 전환합니다."""
    st.session_state.current_page = page
    st.rerun()

# --- Mock 로그인 헬퍼 함수 (추가) ---
def perform_mock_login(user_to_login):
    """지정된 Mock 사용자 데이터로 로그인 처리 후 페이지 이동"""
    if not user_to_login:
        st.error("사용자 정보를 찾을 수 없습니다. Mock 데이터 설정을 확인해 주세요.")
        return
        
    user_data = {**user_to_login}
    user_data.pop('password', None) # 민감 정보 제거
    
    st.session_state.user_data = user_data
    
    with st.spinner("로그인 중..."):
        time.sleep(0.5) # 로그인 애니메이션 효과
        
    st.success(f"로그인 성공! {user_data['studentName']}님 환영합니다. 홈 화면으로 이동합니다.")
    navigate(PAGE_HOME)


# --- 4. 페이지 렌더링 함수 ---

def render_login_page():
    """요청에 따라 두 개의 버튼을 사용하는 로그인 페이지를 렌더링합니다."""
    
    st.markdown(
        """
        <style>
            /* 버튼 중앙 정렬 및 디자인 */
            .stButton>button {
                display: block;
                margin-left: auto;
                margin-right: auto;
                font-size: 1.2rem;
                padding: 15px 30px;
                border-radius: 12px;
                font-weight: bold;
                transition: all 0.2s;
            }
            .stButton:first-child button {
                background-color: #2563eb; /* Blue for Normal User */
                color: white;
            }
            .stButton:nth-child(2) button {
                background-color: #f59e0b; /* Amber for Admin */
                color: white;
            }
            .stButton>button:hover {
                filter: brightness(1.1);
                transform: translateY(-2px);
            }
            .login-container {
                max-width: 400px;
                margin: 50px auto;
                padding: 30px;
                border: 1px solid #e5e7eb;
                border-radius: 16px;
                box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
                background-color: #ffffff;
            }
        </style>
        """, unsafe_allow_html=True
    )
    
    # 중앙 정렬을 위한 컬럼 분할
    col1, col2, col3 = st.columns([1, 4, 1])

    with col2:
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        st.markdown('<h2 style="text-align: center; color: #1e40af; margin-bottom: 30px;">🗺️ Job-Trekking 로그인 💼</h2>', unsafe_allow_html=True)
        
        # 1. 일반 사용자 로그인 버튼
        if st.button("🚀 일반 사용자 로그인 / 시작하기", key="mock_login_normal", use_container_width=True):
            perform_mock_login(st.session_state.mock_user_normal)
            
        st.markdown("<br>", unsafe_allow_html=True) # 공백 추가

        # 2. 관리자 로그인 버튼
        if st.button("⚙️ 관리자 로그인 (데모)", key="mock_login_admin", use_container_width=True):
            perform_mock_login(st.session_state.mock_user)

        st.markdown("---")
        
        # 3. 회원가입 버튼 (네이티브 기능 유지)
        if st.button("회원가입", key="navigate_to_signup", use_container_width=True):
            navigate(PAGE_SIGNUP)
            
        st.markdown('</div>', unsafe_allow_html=True)


def render_signup_page():
    """회원가입 페이지를 Streamlit 네이티브 폼으로 렌더링합니다."""
    st.title("회원가입")

    today = date.today()
    min_date = date(2007, 1, 1)
    default_birth_date = min_date

    with st.form("signup_form"):
        st.write("사용자 정보를 입력해주세요. (가입 시 일반 사용자 권한이 부여됩니다)")
        
        email = st.text_input("이메일 주소", key="signup_email")
        password = st.text_input("비밀번호 (6자 이상)", type="password", key="signup_password")
        st.markdown("---")
        school_name = st.text_input("학교 이름", key="signup_school")
        class_number = st.text_input("반 번호", key="signup_class")
        student_name = st.text_input("이름", key="signup_name")
        
        birth_date = st.date_input(
            "생년월일", 
            value=default_birth_date,
            min_value=min_date,
            max_value=today,
            key="signup_birth",
            format="YYYY.MM.DD"
        )
        
        submitted = st.form_submit_button("회원가입 완료")

        if submitted:
            if not all([email, password, school_name, class_number, student_name, birth_date]):
                st.error("모든 필드를 입력해 주세요.")
            elif len(password) < 6:
                st.error("비밀번호는 6자 이상이어야 합니다.")
            elif birth_date < min_date or birth_date > today:
                st.error("생년월일은 2007년 1월 1일부터 오늘 날짜까지만 선택 가능합니다.")
            else:
                # 일반 사용자 Mock 데이터 저장 (이 정보로 로그인을 시도할 수 있게 됩니다)
                st.session_state.mock_user_normal = {
                    'email': email,
                    'password': password, 
                    'schoolName': school_name,
                    'classNumber': class_number,
                    'studentName': student_name,
                    'birthDate': birth_date.strftime("%Y-%m-%d"),
                    'isAdmin': False # 일반 사용자
                }
                
                st.success(f"{student_name}님, 회원가입이 완료되었습니다! 이제 이 정보로 로그인해 주세요.")
                
                navigate(PAGE_LOGIN)

    st.markdown("---")
    if st.button("로그인 화면으로 돌아가기", key="back_to_login_btn"):
        navigate(PAGE_LOGIN)


def render_home_page():
    """홈 화면을 렌더링합니다. (HTML 컴포넌트 사용)"""
    user_info = st.session_state.user_data
    user_name = user_info.get('studentName', '사용자')
    is_admin = user_info.get('isAdmin', False)
    admin_status = "✅ 관리자" if is_admin else "👤 일반 사용자"

    # 1. 제목과 '잡스리포트 기록하기', '나의 기록 보기', '프로그램 목록 보기' 버튼을 나란히 배치 (수정된 부분)
    col_title, col_button_add, col_button_view, col_button_list = st.columns([2.5, 1, 1, 1])

    with col_title:
        st.title("🗺️ Job-Trekking 홈 💼")
    
    # 버튼을 제목 옆에 세로 중앙에 배치하기 위한 마크다운 공백
    st.markdown("<div style='height: 25px;'></div>", unsafe_allow_html=True) 

    with col_button_add:
        if st.button("📝 리포트 기록하기", key="navigate_to_report_from_home"):
            navigate(PAGE_ADD_REPORT) 

    with col_button_view: 
        if st.button("📖 나의 기록 보기", key="navigate_to_view_reports_from_home"):
            navigate(PAGE_VIEW_REPORTS) # 나의 기록 보기 페이지로 이동

    with col_button_list: 
        if st.button("🔎 프로그램 목록", key="navigate_to_program_list_from_home"):
            navigate(PAGE_PROGRAM_LIST) # 프로그램 목록 보기 페이지로 이동

    st.write(f"환영합니다, **{user_name}**님! 현재 권한: **{admin_status}**")
    
    # 관리자 기능 버튼 추가
    if is_admin:
        if st.button("새 프로그램 추가 (관리자 전용)", key="add_program_btn"):
            navigate(PAGE_ADD_PROGRAM)

    # home.html 파일 읽기
    html_content = read_html_file('home.html')
    
    if html_content:
        # 사용자 이름 등 동적 데이터를 HTML에 주입
        html_content = html_content.replace('{{USER_NAME}}', user_name)
        html_content = html_content.replace('{{USER_SCHOOL}}', user_info.get('schoolName', '학교 정보 없음'))
        html_content = html_content.replace('{{USER_CLASS}}', user_info.get('classNumber', '반 정보 없음'))
        html_content = html_content.replace('{{USER_IS_ADMIN}}', admin_status)
        
        components.html(
            html_content,
            height=700,
            scrolling=True,
        )
    
    st.markdown("---")
    if st.button("로그아웃"):
        st.session_state.user_data = None
        navigate(PAGE_LOGIN)

def render_program_list_page():
    """Firestore에서 프로그램을 로드하고 표시하는 페이지를 렌더링합니다."""
    st.title("진로 프로그램 검색 결과 🔎")
    st.info("이 페이지의 프로그램 목록은 Streamlit 세션의 Mock 데이터로 표시됩니다.")

    # Mock 데이터를 HTML 컴포넌트로 전달하여 표시하도록 할 수 있으나, 
    # 현재는 read_html_file에서 Mock HTML을 반환하도록 처리합니다.

    program_list_html = read_html_file('program_list.html')
    
    if program_list_html:
        # Streamlit 컴포넌트 내에서 사용할 Firebase 설정 변수 주입 (현재 Mock이므로 기능하지 않음)
        program_list_html = program_list_html.replace('{{FIREBASE_CONFIG}}', json.dumps(firebaseConfig))
        program_list_html = program_list_html.replace('{{INITIAL_AUTH_TOKEN}}', initialAuthToken)
        program_list_html = program_list_html.replace('{{APP_ID}}', appId)
        
        components.html(
            program_list_html,
            height=800,
            scrolling=True,
        )

    st.markdown("---")
    if st.button("메인 화면으로 돌아가기", key="back_to_home_from_list"):
        navigate(PAGE_HOME)

def render_add_program_page():
    """관리자가 새 프로그램을 Firestore에 추가할 수 있는 폼을 렌더링합니다."""
    if not st.session_state.user_data or not st.session_state.user_data.get('isAdmin', False):
        st.error("접근 권한이 없습니다.")
        navigate(PAGE_HOME)
        return

    st.title("새 진로 프로그램 추가 (관리자 전용) ✏️")
    st.info("여기에 입력된 프로그램은 Streamlit 세션에 임시로 저장됩니다.")

    add_program_html = read_html_file('add_program.html')

    if add_program_html:
        add_program_html = add_program_html.replace('{{FIREBASE_CONFIG}}', json.dumps(firebaseConfig))
        add_program_html = add_program_html.replace('{{INITIAL_AUTH_TOKEN}}', initialAuthToken)
        add_program_html = add_program_html.replace('{{APP_ID}}', appId)

        components.html(
            add_program_html,
            height=600,
            scrolling=False,
        )
    
    st.markdown("---")
    if st.button("프로그램 목록 보기", key="back_to_list_from_add"):
        navigate(PAGE_PROGRAM_LIST)

def render_add_report_page():
    """
    HTML 컴포넌트로 폼을 표시하고, HTML 버튼을 통해 받은 신호로 저장 처리를 수행합니다.
    (read_html_file의 안정성을 전제하고, 로드 실패 시 명확한 오류 UI를 제공합니다.)
    """
    st.title("잡스리포트 기록하기 📝")
    
    # 1. HTML 컴포넌트 렌더링 (폼 입력 및 제출 버튼 담당)
    add_report_html = read_html_file('add_report.html')
    component_value = None
    
    # --------------------------------------------------------------------------
    # ✨ 최종 방어 로직: add_report_html이 유효한 문자열인지 다시 확인합니다.
    # read_html_file이 빈 문자열을 반환하면 (로드 실패), HTML 컴포넌트 렌더링을 건너뜁니다.
    # --------------------------------------------------------------------------
    if not isinstance(add_report_html, str) or not add_report_html.strip():
        # HTML 로드 실패 시 Streamlit에 오류 메시지를 표시하고, components.html 호출을 건너뜁니다.
        st.error("⚠️ [심각한 오류] 리포트 입력 양식 HTML 파일 ('add_report.html')을 **불러올 수 없습니다**.")
        st.warning("`read_html_file` 함수가 빈 문자열을 반환했습니다. **파일 경로**와 **파일 내용**을 반드시 확인해 주세요.")
        
        st.markdown("---")
        # 오류 상태에서 홈으로 돌아가는 버튼 (다른 버튼들과 key가 겹치지 않도록 명확하게 정의)
        if st.button("메인 화면으로 돌아가기", key="error_back_to_home"):
            # navigate, PAGE_HOME 등의 변수는 외부에서 정의되었다고 가정합니다.
            navigate(PAGE_HOME)
        return
    # --------------------------------------------------------------------------
    
    # HTML이 유효한 문자열일 경우에만 component.html을 호출합니다. (Line 609 주변)
    # 이 로직을 통과하면 TypeError는 발생하지 않아야 합니다.
    component_value = components.html(
        html=add_report_html, 
        height=700, # 버튼이 포함되었으므로 높이 증가
        scrolling=True,
        # Streamlit-Component-Lib를 위한 key 설정
        key="add_report_form_component"
    )

    # 2. HTML 컴포넌트로부터 전달받은 데이터 추출 및 처리
    current_data = None
    is_submitted = False
    
    # component_value가 딕셔너리 형태이고 'reportData' 키를 포함하는지 확인합니다.
    if isinstance(component_value, dict) and 'reportData' in component_value:
        current_data = component_value['reportData']
        # 'submitted' 플래그는 HTML의 버튼 클릭 시에만 True로 설정됩니다.
        is_submitted = component_value.get('submitted', False)

    # 3. Streamlit 상태 관리 및 저장 로직 (HTML 제출 신호 대기)
    st.markdown("---")

    # A) 저장 성공 후 상태
    if st.session_state.get('report_saved_successfully', False):
        # 성공 메시지 표시
        st.success("🎉 리포트가 성공적으로 저장되었습니다. 다음 활동을 선택해 주세요.")
        
        # NOTE: 페이지 이동 전에 False로 초기화하여 다음 렌더링 시 메시지가 다시 뜨지 않게 합니다.
        st.session_state.report_saved_successfully = False 
        
        # PAGE_VIEW_REPORTS 변수는 외부에서 정의되었다고 가정합니다.
        col_view, col_home = st.columns(2)
        with col_view:
            if st.button("📖 나의 기록 보기", key="post_save_view_reports"):
                navigate(PAGE_VIEW_REPORTS)
        with col_home:
            if st.button("메인 화면으로 돌아가기", key="post_save_home"):
                navigate(PAGE_HOME)

    # B) 제출 신호 수신 상태 (HTML 버튼 클릭)
    elif is_submitted and current_data:
        # 필수 필드 체크: programName, experienceDate, rating, reportContent
        is_valid = (
            current_data.get('programName') and 
            current_data.get('experienceDate') and 
            current_data.get('rating') is not None and 
            current_data.get('reportContent')
        )

        if is_valid:
            
            # 저장 로직 실행
            # save_report_to_firestore 함수는 외부에서 정의되었다고 가정합니다.
            success, message = save_report_to_firestore(current_data)
            
            if success:
                st.session_state.report_saved_successfully = True
                st.session_state.current_report_data = None # 임시 데이터 초기화
                st.rerun() # 성공 메시지와 버튼을 표시하기 위해 페이지 새로고침
            else:
                st.error(f"⚠️ 리포트 저장 실패: {message}")
        else:
            # HTML에서 데이터가 넘어왔지만, 필수 필드가 비어있을 때
            st.error("⚠️ 폼 데이터가 준비되지 않았습니다. 모든 필수 항목(프로그램명, 일자, 별점, 소감)을 입력했는지 확인해 주세요.")


    # C) 기본 상태 (제출 신호가 없을 때, HTML 로드 성공 시)
    elif component_value is not None and not st.session_state.get('report_saved_successfully', False):
        st.markdown("---")
        if st.button("메인 화면으로 돌아가기", key="back_to_home_from_report_default"):
            navigate(PAGE_HOME)
            
def render_view_reports_page():
    """
    사용자가 기록한 잡스리포트 목록을 보고 상세 내용을 확인하는 페이지를 렌더링합니다.
    Streamlit Python 백엔드의 임시 저장소(`firestore_reports`)를 사용합니다.
    """
    st.title("나의 진로 체험 기록 📖")
    st.info("이 페이지에서는 지금까지 작성한 잡스리포트 목록을 볼 수 있습니다. (개인 기록)")
    
    user_id = get_current_user_id()
    if not user_id:
        st.error("사용자 인증 정보를 찾을 수 없습니다. 로그인 상태를 확인해 주세요.")
        return

    # Python 백엔드 임시 저장소에서 리포트 로드
    all_reports = st.session_state.firestore_reports.get(user_id, [])
    
    if not all_reports:
        st.markdown("""
            <div style="text-align: center; color: #6b7280; padding: 40px; border: 2px dashed #d1d5db; border-radius: 12px; margin-top: 20px;">
                <svg xmlns="http://www.w3.org/2000/svg" class="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" style="display: block; margin: 0 auto 10px auto; width: 48px; height: 48px;"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/></svg>
                <h3 style="font-size: 1.25rem; font-weight: 600; color: #1f2937;">작성된 리포트가 없습니다</h3>
                <p style="margin-top: 5px; font-size: 0.875rem;">지금 바로 잡스리포트를 작성해 보세요!</p>
            </div>
        """, unsafe_allow_html=True)
        
    else:
        # 최신순 정렬 (createdAt은 ISO 문자열이므로 역순 정렬)
        sorted_reports = sorted(all_reports, key=lambda x: x['createdAt'], reverse=True)
        
        st.sidebar.header("리포트 목록")
        st.sidebar.markdown(f"총 **{len(sorted_reports)}**건의 기록이 있습니다.")

        # Streamlit Selectbox를 사용하여 리포트 선택
        report_titles = [f"{r['experienceDate']} - {r['programName']}" for r in sorted_reports]
        
        # 선택 목록이 비어있지 않은 경우에만 selectbox 표시
        if report_titles:
            selected_title = st.sidebar.selectbox("리포트 선택", report_titles)

            # 선택된 리포트 찾기
            selected_report_index = report_titles.index(selected_title)
            selected_report = sorted_reports[selected_report_index]

            # 5. 별점 렌더링 함수
            def get_rating_stars(rating):
                return "<span style='color: #fbbf24;'>★</span>" * rating + "<span style='color: #ccc;'>☆</span>" * (5 - rating)

            # 상세 리포트 뷰 (선택된 리포트 표시)
            st.markdown("---")
            st.subheader(f"선택된 리포트: {selected_report['programName']}")
            
            col_date, col_field = st.columns(2)
            with col_date:
                st.markdown(f"**체험 일자:** `{selected_report['experienceDate']}`")
            with col_field:
                st.markdown(f"**분야:** `{selected_report['jobField']}`")

            st.markdown("---")
            st.markdown("### 체험 만족도")
            # 별점은 1~5 사이의 정수여야 함
            rating = selected_report.get('rating', 0)
            rating = max(0, min(5, rating))
            st.markdown(f"<p style='font-size: 2rem;'>{get_rating_stars(rating)}</p>", unsafe_allow_html=True)
            
            st.markdown("### 소감 및 내용")
            st.markdown(f'<div style="background-color: #f7f7f7; padding: 15px; border-radius: 8px; white-space: pre-wrap; border-left: 5px solid #10b981;">{selected_report["reportContent"]}</div>', unsafe_allow_html=True)
        else:
             st.info("선택할 수 있는 리포트가 없습니다.")


    st.markdown("---")
    if st.button("메인 화면으로 돌아가기", key="back_to_home_from_view_reports"):
        navigate(PAGE_HOME)


# --- 5. 메인 렌더링 루프 ---

current_user_authenticated = (st.session_state.user_data is not None)

if st.session_state.current_page == PAGE_LOGIN:
    render_login_page()
elif st.session_state.current_page == PAGE_SIGNUP:
    render_signup_page()
elif st.session_state.current_page == PAGE_HOME and current_user_authenticated:
    render_home_page()
elif st.session_state.current_page == PAGE_PROGRAM_LIST and current_user_authenticated:
    render_program_list_page()
elif st.session_state.current_page == PAGE_ADD_PROGRAM and current_user_authenticated:
    render_add_program_page()
elif st.session_state.current_page == PAGE_ADD_REPORT and current_user_authenticated:
    render_add_report_page()
elif st.session_state.current_page == PAGE_VIEW_REPORTS and current_user_authenticated: # 신규 페이지 처리
    render_view_reports_page()
else:
    # 인증되지 않은 상태에서 접근 시 로그인 페이지로 리다이렉션
    st.session_state.current_page = PAGE_LOGIN
    navigate(PAGE_LOGIN)

st.sidebar.markdown(f"**현재 로드 중인 페이지:** {st.session_state.current_page.upper()}")



