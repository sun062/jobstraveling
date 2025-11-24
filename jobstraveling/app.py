import streamlit as st
import streamlit.components.v1 as components
import os
import json 
from datetime import date, datetime 

# --- Firebase SDK Admin (Python) 사용을 위한 Stubs ---
# Python에서 Firestore에 접근하기 위해 가상의 함수를 정의합니다.
# 실제 Firebase Admin SDK를 가져올 수 없으므로, on-premise 환경에서는
# 이 부분이 실제 데이터베이스 접근 로직으로 대체됩니다.
# 이 환경에서는 Streamlit이 백엔드 역할을 하므로, `st.session_state`에
# 임시 데이터베이스 스텁을 만들어 사용하겠습니다.
if 'firestore_reports' not in st.session_state:
    st.session_state.firestore_reports = {} # {userId: [report1, report2, ...]}

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
PAGE_ADD_REPORT = 'add_report'     # 잡스리포트 기록 페이지 (Streamlit 폼으로 변경)
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

    # Firestore Data Structure Stub
    if user_id not in st.session_state.firestore_reports:
        st.session_state.firestore_reports[user_id] = []
    
    report_data['id'] = str(len(st.session_state.firestore_reports[user_id]) + 1) # 임시 ID 부여
    report_data['createdAt'] = datetime.now().isoformat()
    
    st.session_state.firestore_reports[user_id].append(report_data)
    
    st.success("✅ 리포트가 성공적으로 저장되었습니다.")
    return True, ""


# --- 2. HTML 파일 로드 함수 ---
def read_html_file(file_name):
    """HTML 파일을 읽어 문자열로 반환합니다. (htmls 폴더 내에서 파일을 찾습니다)"""
    file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'htmls', file_name)
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        st.error(f"HTML 파일을 찾을 수 없습니다. 경로를 확인해주세요: {file_path}")
        return ""

# --- 3. 페이지 전환 ---
def navigate(page):
    """세션 상태를 변경하여 페이지를 전환합니다."""
    st.session_state.current_page = page
    st.rerun()

# --- 4. 페이지 렌더링 함수 ---

# (render_login_page, render_signup_page, render_home_page, render_program_list_page, render_add_program_page는 변경 없음)

def render_login_page():
    """로그인 페이지를 Streamlit 네이티브 폼으로 렌더링합니다."""
    st.title("로그인")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("login_form", clear_on_submit=False):
            st.markdown('<h3 style="text-align: center; color: #3b82f6;">Job-Trekking 로그인</h3>', unsafe_allow_html=True)
            
            st.info("💡 **팁:** 관리자 계정: `admin@jobtrekking.com`/`adminpassword` | 일반 계정: `user@jobtrekking.com`/`userpassword`")
            
            email = st.text_input("이메일 주소", key="login_email")
            password = st.text_input("비밀번호", type="password", key="login_password")
            
            login_submitted = st.form_submit_button("로그인")
            
            if login_submitted:
                if not all([email, password]):
                    st.error("이메일과 비밀번호를 모두 입력해 주세요.")
                    return
                
                # Mock 로그인 처리 (관리자 또는 일반 사용자 계정 대조)
                user_to_check = None
                if email == st.session_state.mock_user['email']:
                    user_to_check = st.session_state.mock_user
                elif email == st.session_state.mock_user_normal['email']:
                    user_to_check = st.session_state.mock_user_normal
                elif email == st.session_state.mock_user.get('email', 'N/A') and password == st.session_state.mock_user.get('password', 'N/A'):
                    user_to_check = st.session_state.mock_user 

                if (user_to_check and 
                    user_to_check.get('password') == password):
                    
                    st.success("로그인 성공! 홈 화면으로 이동합니다.")
                    
                    # Mock 사용자 데이터에서 민감 정보(password) 제거 후 저장
                    user_data = {**user_to_check}
                    user_data.pop('password', None)
                    st.session_state.user_data = user_data
                    
                    navigate(PAGE_HOME)
                    
                else:
                    st.error("이메일 또는 비밀번호가 올바르지 않습니다.")

        if st.button("회원가입", key="navigate_to_signup"):
            navigate(PAGE_SIGNUP)


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

    # 1. 제목과 '잡스리포트 기록하기', '나의 기록 보기' 버튼을 나란히 배치 (요청 사항)
    col_title, col_button_add, col_button_view = st.columns([3, 1, 1])

    with col_title:
        st.title("🗺️ Job-Trekking 홈 💼")
    
    with col_button_add:
        # 버튼을 제목 옆에 세로 중앙에 배치하기 위한 마크다운 공백
        st.markdown("<div style='height: 25px;'></div>", unsafe_allow_html=True) 
        if st.button("📝 잡스리포트 기록하기", key="navigate_to_report_from_home"):
            navigate(PAGE_ADD_REPORT) 

    with col_button_view: 
        st.markdown("<div style='height: 25px;'></div>", unsafe_allow_html=True) 
        if st.button("📖 나의 기록 보기", key="navigate_to_view_reports_from_home"):
            navigate(PAGE_VIEW_REPORTS) # 나의 기록 보기 페이지로 이동

    st.write(f"환영합니다, **{user_name}**님! 아래는 **'홈 화면'**의 콘텐츠입니다.")
    
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
    st.info("이 페이지의 프로그램 목록은 Firebase Firestore에서 실시간으로 로드됩니다.")

    program_list_html = read_html_file('program_list.html')
    
    if program_list_html:
        # Streamlit 컴포넌트 내에서 사용할 Firebase 설정 변수 주입
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
    st.info("여기에 입력된 프로그램은 Firestore에 저장되어 실시간 목록에 반영됩니다.")

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
    사용자가 직업 체험 후기 (잡스리포트)를 기록하는 페이지를 렌더링합니다.
    HTML 컴포넌트 대신 Streamlit 네이티브 폼을 사용하여 안정성을 높였습니다.
    """
    st.title("잡스리포트 기록하기 📝")
    st.info("체험한 내용을 기록하고 별점 평가를 남겨주세요. 리포트는 개인 기록으로 저장됩니다.")
    
    # 별점 선택을 위한 Helper 함수
    def get_rating_stars(rating):
        return "★" * rating + "☆" * (5 - rating)

    with st.form("add_report_form", clear_on_submit=True):
        
        st.markdown("### 1. 체험 정보")
        program_name = st.text_input("체험 프로그램/기관명", key="report_program_name", placeholder="예: 구글 코리아 견학, IT 개발자 직무 체험")
        
        col1, col2 = st.columns(2)
        with col1:
            experience_date = st.date_input("체험 일자", key="report_experience_date", max_value=date.today())
        with col2:
            job_field = st.text_input("직무/분야", key="report_job_field", placeholder="예: 소프트웨어 엔지니어, 마케팅")

        st.markdown("---")
        st.markdown("### 2. 체험 만족도")
        # Streamlit 슬라이더를 사용하여 별점 입력 받기
        rating = st.slider("별점 (5점 만점)", min_value=1, max_value=5, value=5, step=1, key="report_rating", 
                            format=f"%d점 ({get_rating_stars(st.session_state.report_rating)})")

        st.markdown("---")
        st.markdown("### 3. 상세 기록")
        report_content = st.text_area("체험 내용 및 소감", key="report_content", height=200, 
                                      placeholder="체험에서 배운 점, 느낀 점, 좋았던 점, 아쉬웠던 점 등을 상세하게 기록해 주세요. (최소 100자 권장)")
        
        submitted = st.form_submit_button("리포트 저장하기")

        if submitted:
            # 필수 필드 유효성 검사
            if not program_name or not experience_date or not report_content:
                st.error("⚠️ 체험 프로그램명, 체험 일자, 소감 내용을 모두 입력해 주세요.")
                return

            # 데이터 저장
            report_data = {
                'programName': program_name,
                'experienceDate': experience_date.strftime("%Y-%m-%d"),
                'jobField': job_field,
                'rating': rating,
                'reportContent': report_content,
            }

            # Python 백엔드에서 데이터 저장 시뮬레이션
            success, message = save_report_to_firestore(report_data)

            if success:
                # 저장 성공 후 다음 활동 선택 화면 (요청 사항)
                st.session_state.report_saved_successfully = True
                st.success("🎉 리포트가 성공적으로 저장되었습니다. 다음 활동을 선택해 주세요.")
                st.markdown("---")
            else:
                st.error(f"저장 실패: {message}")
    
    # 저장 성공 후 활동 선택 버튼 표시
    if st.session_state.get('report_saved_successfully', False):
        st.markdown("<div class='flex flex-col space-y-3 mt-4'>", unsafe_allow_html=True)
        col_view, col_home = st.columns(2)
        with col_view:
            if st.button("📖 나의 기록 보기", key="post_save_view_reports"):
                st.session_state.report_saved_successfully = False # 상태 초기화
                navigate(PAGE_VIEW_REPORTS)
        with col_home:
            if st.button("메인 화면으로 돌아가기", key="post_save_home"):
                st.session_state.report_saved_successfully = False # 상태 초기화
                navigate(PAGE_HOME)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("---")
    if st.button("메인 화면으로 돌아가기", key="back_to_home_from_report_default"):
        navigate(PAGE_HOME)

def render_view_reports_page():
    """
    사용자가 기록한 잡스리포트 목록을 보고 상세 내용을 확인하는 페이지를 렌더링합니다.
    Streamlit Python 백엔드의 임시 저장소(`firestore_reports`)를 사용하도록 변경합니다.
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
            <div class="text-center text-gray-500 p-10 bg-white rounded-xl shadow-lg border border-dashed border-gray-300 mt-10">
                <svg xmlns="http://www.w3.org/2000/svg" class="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/></svg>
                <h3 class="mt-2 text-lg font-medium text-gray-900">작성된 리포트가 없습니다</h3>
                <p class="mt-1 text-sm text-gray-500">지금 바로 잡스리포트를 작성해 보세요!</p>
            </div>
        """, unsafe_allow_html=True)
        
    else:
        # 최신순 정렬 (createdAt은 ISO 문자열이므로 역순 정렬)
        sorted_reports = sorted(all_reports, key=lambda x: x['createdAt'], reverse=True)
        
        st.sidebar.header("리포트 목록")
        st.sidebar.markdown(f"총 **{len(sorted_reports)}**건의 기록이 있습니다.")

        # Streamlit Selectbox를 사용하여 리포트 선택
        report_titles = [f"{r['experienceDate']} - {r['programName']}" for r in sorted_reports]
        selected_title = st.sidebar.selectbox("리포트 선택", report_titles)

        # 선택된 리포트 찾기
        selected_report_index = report_titles.index(selected_title)
        selected_report = sorted_reports[selected_report_index]

        # 5. 별점 렌더링 함수
        def get_rating_stars(rating):
            return "★" * rating + "☆" * (5 - rating)

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
        st.markdown(f"<p style='font-size: 2rem; color: #fbbf24;'>{get_rating_stars(selected_report['rating'])}</p>", unsafe_allow_html=True)
        
        st.markdown("### 소감 및 내용")
        st.markdown(f'<div style="background-color: #f7f7f7; padding: 15px; border-radius: 8px; white-space: pre-wrap;">{selected_report["reportContent"]}</div>', unsafe_allow_html=True)

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
