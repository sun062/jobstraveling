import streamlit as st
import streamlit.components.v1 as components
import os
import json 
from datetime import date, datetime 

# --- Firebase SDK Admin (Python) 사용을 위한 Stubs ---
# 이 환경에서는 Streamlit이 백엔드 역할을 하므로, `st.session_state`에
# 임시 데이터베이스 스텁을 만들어 사용하겠습니다. (기존 로직 유지)
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
PAGE_ADD_REPORT = 'add_report'     # 잡스리포트 기록 페이지
PAGE_VIEW_REPORTS = 'view_reports' # 잡스리포트 목록/상세 보기 페이지

# 세션 상태 초기화 (Mock 데이터 포함)
if 'current_page' not in st.session_state:
    st.session_state.current_page = PAGE_LOGIN
if 'user_data' not in st.session_state:
    st.session_state.user_data = None # 로그인한 사용자 정보
if 'mock_user' not in st.session_state:
    st.session_state.mock_user = {
        'email': 'admin@jobtrekking.com', 
        'password': 'adminpassword',
        'schoolName': '관리자 학교',
        'classNumber': '999',
        'studentName': '관리자',
        'birthDate': '2000-01-01',
        'isAdmin': True 
    }
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
    """Mock User ID 반환."""
    return st.session_state.user_data.get('email') if st.session_state.user_data else None

def save_report_to_firestore(report_data):
    """
    Python 백엔드에서 리포트 데이터를 저장합니다.
    실제 Firestore SDK 없이 세션 상태를 임시 저장소로 사용합니다.
    """
    user_id = get_current_user_id()
    if not user_id:
        return False, "사용자 인증 정보를 찾을 수 없습니다."

    # 필수 필드 유효성 검사 
    if not report_data or not report_data.get('programName') or not report_data.get('experienceDate') or report_data.get('rating') is None or not report_data.get('reportContent'):
        return False, "체험 프로그램명, 일자, 별점, 소감 내용을 모두 입력해 주세요."
    
    # Firestore Data Structure Stub
    if user_id not in st.session_state.firestore_reports:
        st.session_state.firestore_reports[user_id] = []
    
    report_data['id'] = str(len(st.session_state.firestore_reports[user_id]) + 1) # 임시 ID 부여
    report_data['createdAt'] = datetime.now().isoformat()
    
    st.session_state.firestore_reports[user_id].append(report_data)
    
    return True, ""


# --- 2. HTML 파일 로드 함수 ---
def read_html_file(file_name):
    """HTML 파일을 읽어 문자열로 반환합니다. (htmls 폴더 내에서 파일을 찾습니다)"""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, 'htmls', file_name)
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            if not content:
                st.warning(f"파일이 성공적으로 로드되었으나 내용이 비어 있습니다: 'htmls/{file_name}'")
            return content # str 타입 그대로 반환
    except FileNotFoundError:
        st.error(f"⚠️ HTML 파일을 찾을 수 없습니다. 'htmls/{file_name}' 경로를 확인해 주세요.")
        return "" # 파일을 찾지 못하면 빈 문자열 반환
    except Exception as e:
        st.error(f"파일 읽기 중 예기치 않은 오류 발생: {e}")
        return ""

# --- 3. 페이지 전환 ---
def navigate(page):
    """세션 상태를 변경하여 페이지를 전환합니다."""
    st.session_state.current_page = page
    st.rerun()

# --- 4. 페이지 렌더링 함수 ---

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
                
                user_to_check = None
                if email == st.session_state.mock_user['email']:
                    user_to_check = st.session_state.mock_user
                elif email == st.session_state.mock_user_normal['email']:
                    user_to_check = st.session_state.mock_user_normal

                if (user_to_check and 
                    user_to_check.get('password') == password):
                    
                    st.success("로그인 성공! 홈 화면으로 이동합니다.")
                    
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
                st.session_state.mock_user_normal = {
                    'email': email,
                    'password': password, 
                    'schoolName': school_name,
                    'classNumber': class_number,
                    'studentName': student_name,
                    'birthDate': birth_date.strftime("%Y-%m-%d"),
                    'isAdmin': False
                }
                
                st.success(f"{student_name}님, 회원가입이 완료되었습니다! 이제 이 정보로 로그인해 주세요.")
                
                navigate(PAGE_LOGIN)

    st.markdown("---")
    if st.button("로그인 화면으로 돌아가기", key="back_to_login_btn"):
        navigate(PAGE_LOGIN)

def render_home_page():
    """홈 화면을 렌더링합니다. (기존 구조 복원)"""
    user_info = st.session_state.user_data
    user_name = user_info.get('studentName', '사용자')
    is_admin = user_info.get('isAdmin', False)

    st.title("🗺️ Job-Trekking 홈 💼")
    st.write(f"환영합니다, **{user_name}**님!")

    # 페이지 이동 버튼들 (Streamlit 네이티브 버튼)
    if st.button("📝 잡스리포트 기록하기", key="navigate_to_report"):
        navigate(PAGE_ADD_REPORT) 
        
    if st.button("📖 나의 기록 보기", key="navigate_to_view_reports"):
        navigate(PAGE_VIEW_REPORTS) # 나의 기록 보기 페이지로 이동

    if st.button("🔎 프로그램 목록 보기", key="navigate_to_program_list"):
        navigate(PAGE_PROGRAM_LIST) # 프로그램 목록 보기 페이지로 이동

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
            height=300, # 높이를 줄여서 Streamlit 버튼과 잘 보이게 조정
            scrolling=False,
        )
    
    st.markdown("---")
    if st.button("로그아웃"):
        st.session_state.user_data = None
        navigate(PAGE_LOGIN)

def render_program_list_page():
    """프로그램 목록 페이지 (기존 로직 유지)"""
    st.title("진로 프로그램 검색 결과 🔎")
    st.info("이 페이지의 프로그램 목록은 Firebase Firestore에서 실시간으로 로드됩니다.")

    program_list_html = read_html_file('program_list.html')
    
    if program_list_html:
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
    """새 프로그램 추가 페이지 (기존 로직 유지)"""
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
    HTML 컴포넌트로 폼 입력만 표시하고, Streamlit 네이티브 버튼으로 저장 처리를 수행합니다.
    """
    st.title("잡스리포트 기록하기 📝")
    
    # 1. HTML 컴포넌트 렌더링 (폼 입력만 담당)
    add_report_html = read_html_file('add_report.html')
    
    component_value = None
    
    # **최강 방어 로직**: HTML 콘텐츠를 str()로 강제 변환하고, 그 내용이 비어있지 않은 경우에만 호출
    html_content_safe = str(add_report_html) if add_report_html is not None else ""

    if html_content_safe.strip():
        try:
            # **수정**: 'key' 인수를 제거하여 Streamlit 내부 오류를 회피
            component_value = components.html(
                html=html_content_safe,  # 안전하게 변환된 문자열 전달
                height=700, 
                scrolling=True,
                # key="report_form_component"  <-- 이 인수를 제거했습니다.
            )
        except Exception as e:
            # Streamlit 내부 오류 발생 시에도 앱이 다운되지 않도록 처리
            st.error(f"⚠️ 컴포넌트 렌더링 중 Streamlit 내부 오류 발생: {e}. HTML 파일 내용을 다시 확인해 주세요.")
            st.info(f"시도된 HTML 길이: {len(html_content_safe)}")
    else:
        # 파일 로드 실패 시, 사용자에게 명확히 알림 
        st.error(f"⚠️ 심각: 리포트 폼 HTML 파일(htmls/add_report.html)을 로드할 수 없거나 내용이 비어 있습니다. (길이: {len(html_content_safe)})")
        st.info("HTML 폼이 표시되지 않아 리포트 저장 기능을 사용할 수 없습니다. 파일 경로가 올바른지 확인해 주세요.")


    # 2. HTML 컴포넌트로부터 전달받은 데이터 추출 및 상태 업데이트
    current_data = None
    if isinstance(component_value, dict) and 'reportData' in component_value:
        current_data = component_value['reportData']
        # 데이터를 세션 상태에 저장하여 Streamlit 버튼 클릭 시 사용
        st.session_state.current_report_data = current_data 
    
    # 디버깅 정보: 현재 세션에 저장된 폼 데이터 확인
    # st.sidebar.json(st.session_state.get('current_report_data'))


    st.markdown("---")

    # 3. Streamlit 네이티브 버튼 (저장 로직 트리거)
    if st.button("🚀 리포트 저장하기", key="submit_report_button"):
        
        # 버튼 클릭 시, HTML 컴포넌트가 마지막으로 전달한 데이터를 사용
        data_to_save = st.session_state.get('current_report_data')

        # 필수 필드 유효성 검사
        is_valid = (
            data_to_save and 
            data_to_save.get('programName') and 
            data_to_save.get('experienceDate') and 
            data_to_save.get('rating') is not None and 
            data_to_save.get('reportContent')
        )

        if is_valid:
            
            success, message = save_report_to_firestore(data_to_save)
            
            if success:
                st.session_state.report_saved_successfully = True
                # 저장 후 현재 폼 데이터를 초기화
                st.session_state.current_report_data = None 
                st.rerun() # 성공 메시지를 표시하기 위해 다시 실행
            else:
                st.error(f"⚠️ 리포트 저장 실패: {message}")
        else:
            st.error("⚠️ 폼 데이터가 준비되지 않았습니다. 모든 필수 항목(프로그램명, 일자, 별점, 소감)을 입력했는지 확인해 주세요.")


    # 4. 저장 성공 후 상태 (성공 메시지 및 네비게이션 버튼)
    if st.session_state.get('report_saved_successfully', False):
        st.success("🎉 리포트가 성공적으로 저장되었습니다. 다음 활동을 선택해 주세요.")
        # 성공 메시지를 한 번만 표시하도록 상태 초기화
        st.session_state.report_saved_successfully = False 
        
        col_view, col_home = st.columns(2)
        with col_view:
            if st.button("📖 나의 기록 보기", key="post_save_view_reports"):
                navigate(PAGE_VIEW_REPORTS)
        with col_home:
            if st.button("메인 화면으로 돌아가기", key="post_save_home"):
                navigate(PAGE_HOME)

    st.markdown("---")
    if st.button("메인 화면으로 돌아가기", key="back_to_home_from_report_default"):
        navigate(PAGE_HOME)

def render_view_reports_page():
    """
    사용자가 기록한 잡스리포트 목록을 보고 상세 내용을 확인하는 페이지를 렌더링합니다.
    (간결한 Streamlit 네이티브 디자인으로 복구)
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
        st.markdown(
            "<div style='text-align: center; padding: 20px; background-color: #f0f0f5; border-radius: 8px;'>"
            "<strong>작성된 리포트가 없습니다.</strong><br>지금 바로 '잡스리포트 기록하기'를 통해 기록을 시작해 보세요!"
            "</div>", unsafe_allow_html=True
        )
        
    else:
        # 최신순 정렬
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
                # 별점은 1~5 사이의 정수여야 함
                rating = max(0, min(5, rating))
                return "★" * rating + "☆" * (5 - rating)

            # 상세 리포트 뷰 (선택된 리포트 표시 - 깔끔한 Streamlit 디자인)
            st.markdown("---")
            st.subheader(f"✅ {selected_report['programName']}")
            
            col_date, col_field = st.columns(2)
            with col_date:
                st.markdown(f"**체험 일자:** `{selected_report['experienceDate']}`")
            with col_field:
                st.markdown(f"**분야:** `{selected_report['jobField'] or '미입력'}`")

            st.markdown("---")
            st.markdown("#### 체험 만족도")
            st.markdown(f"<p style='font-size: 2rem; color: #fbbf24;'>{get_rating_stars(selected_report.get('rating', 0))}</p>", unsafe_allow_html=True)
            
            st.markdown("#### 소감 및 내용")
            st.markdown(f'<div style="background-color: #f7f7f7; padding: 15px; border-radius: 8px; white-space: pre-wrap; border: 1px solid #ddd;">{selected_report["reportContent"]}</div>', unsafe_allow_html=True)
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
elif st.session_state.current_page == PAGE_VIEW_REPORTS and current_user_authenticated:
    render_view_reports_page()
else:
    st.session_state.current_page = PAGE_LOGIN
    navigate(PAGE_LOGIN)

st.sidebar.markdown(f"**현재 로드 중인 페이지:** {st.session_state.current_page.upper()}")
