import streamlit as st
import streamlit.components.v1 as components
import os
import json 
import time
from datetime import date, datetime 
from typing import List, Dict, Any

# --- Firebase SDK Admin (Python) 사용을 위한 Stubs ---
# 이 환경에서는 Streamlit이 백엔드 역할을 하므로, `st.session_state`에
# 임시 데이터베이스 스텁을 만들어 사용하겠습니다. (기존 로직 유지)
if 'firestore_reports' not in st.session_state:
    st.session_state.firestore_reports = {} # {userId: [report1, report2, ...]}

# ⭐️ 프로그램 데이터는 이제 검색을 통해 로드되므로 Mocking 목록은 필요하지 않습니다. ⭐️
if 'search_results' not in st.session_state:
    st.session_state.search_results = []

# --- Global Environment Variables ---
firebaseConfig = json.loads(os.environ.get('__firebase_config', '{}'))
appId = os.environ.get('__app_id', 'default-app-id')
initialAuthToken = os.environ.get('__initial_auth_token', '')

# --- 1. 환경 설정 및 세션 상태 초기화 ---
st.set_page_config(layout="centered", initial_sidebar_state="expanded")

# 페이지 정의 상수
PAGE_LOGIN = 'login'
PAGE_SIGNUP = 'signup'
PAGE_HOME = 'home'
PAGE_PROGRAM_LIST = 'program_list' # ⭐️ 이제 실시간 검색 페이지로 사용됩니다. ⭐️
PAGE_ADD_REPORT = 'add_report'     # 잡스리포트 기록 페이지
PAGE_VIEW_REPORTS = 'view_reports' # 잡스리포트 목록/상세 보기 페이지

# 세션 상태 초기화 (Mock 데이터 포함)
if 'current_page' not in st.session_state:
    st.session_state.current_page = PAGE_LOGIN
if 'user_data' not in st.session_state:
    st.session_state.user_data = None # 로그인한 사용자 정보
# ... (기존 mock_user 및 mock_user_normal 정의는 유지)
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
    st.session_state.current_report_data = {}
if 'report_saved_successfully' not in st.session_state:
    st.session_state.report_saved_successfully = False


# --- Firebase Stubs (Python Backend) ---

def get_current_user_id():
    """Mock User ID 반환."""
    return st.session_state.user_data.get('email') if st.session_state.user_data else None

def save_report_to_firestore(report_data):
    """
    Python 백엔드에서 리포트 데이터를 저장합니다.
    (세션 상태를 임시 저장소로 사용)
    """
    user_id = get_current_user_id()
    if not user_id:
        return False, "사용자 인증 정보를 찾을 수 없습니다."

    # 필수 필드 유효성 검사 
    if not report_data or \
       not report_data.get('programName') or \
       not report_data.get('experienceDate') or \
       report_data.get('rating') is None or \
       not report_data.get('reportContent'):
        return False, "체험 프로그램명, 일자, 별점, 소감 내용을 모두 입력해 주세요."
    
    # Firestore Data Structure Stub
    if user_id not in st.session_state.firestore_reports:
        st.session_state.firestore_reports[user_id] = []
    
    # 중복 방지를 위해 기존 ID 확인 후 부여 (Mocking 환경)
    report_data['id'] = f"R{len(st.session_state.firestore_reports[user_id]) + 1}_{user_id[:3]}" 
    report_data['createdAt'] = datetime.now().isoformat()
    
    st.session_state.firestore_reports[user_id].append(report_data)
    
    return True, ""

# ⭐️ 관리자 프로그램 등록 함수 (save_program_to_firestore)는 제거되었습니다. ⭐️


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
            return content
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

# --- 4. Gemini API 호출 및 구조화 함수 ⭐️ New Feature ⭐️ ---

@st.cache_data(show_spinner="🔍 실시간 진로 프로그램 정보 검색 및 구조화 중...")
def search_and_structure_programs(search_query: str) -> List[Dict[str, Any]]:
    """
    Google Search를 통해 진로 프로그램 정보를 검색하고, Gemini API를 사용하여 
    결과를 정해진 JSON 구조로 추출합니다.
    """
    if not search_query.strip():
        return []
        
    # 1. Google Search API 호출
    # 한국어와 영어 쿼리를 동시에 사용하여 검색 정확도를 높입니다.
    english_query = f"career experience programs {search_query}"
    korean_query = f"진로 체험 프로그램 {search_query}"
    
    # 실제 Google Search 호출 (이 함수는 런타임에 도구로 대체됩니다)
    try:
        # ⭐️ Search Tool Call Simulation (이 부분은 실제 환경에서 호출됩니다) ⭐️
        search_result_text = google.search(queries=[english_query, korean_query])
    except Exception as e:
        st.error(f"Google 검색 API 호출 실패: {e}")
        return []
    
    if not search_result_text:
        return []

    # 2. Gemini API를 사용하여 검색 결과를 구조화
    system_prompt = (
        "당신은 교육 컨설턴트입니다. 제공된 검색 결과에서 한국의 '진로 체험' 또는 '견학' 프로그램 정보를 추출하여 "
        "다음 JSON 스키마에 따라 응답하세요. 프로그램명, 분야, 장소, 운영기관, 모집 상태, 참고 링크 6가지 항목만 추출해야 합니다. "
        "모집 상태는 '모집 중', '모집 마감', '모집 예정', '종료' 중 하나로 판단하세요. "
        "추출할 수 없는 정보는 '정보 없음'으로 표시하며, 링크는 가능한 한 가장 직접적인 프로그램 페이지 링크를 사용하세요. "
        "결과가 없으면 빈 배열을 반환하세요."
    )
    
    user_query = (
        f"사용자의 검색어는 '{search_query}'입니다. 다음 검색 결과를 바탕으로 관련된 진로 프로그램 목록을 JSON 배열로 구조화해 주세요.\n\n"
        f"--- 검색 결과 ---\n{search_result_text}"
    )

    # JSON 스키마 정의 (원하는 출력 구조)
    response_schema = {
        "type": "ARRAY",
        "items": {
            "type": "OBJECT",
            "properties": {
                "programName": {"type": "STRING", "description": "프로그램의 공식 명칭"},
                "jobField": {"type": "STRING", "description": "관련 직업/분야 (예: IT, 의료, 환경)"},
                "location": {"type": "STRING", "description": "장소/진행 방식 (예: 서울, 온라인, 대전 카이스트)"},
                "host": {"type": "STRING", "description": "주최/운영 기관"},
                "status": {"type": "STRING", "description": "현재 모집 상태 ('모집 중', '모집 마감', '모집 예정', '종료' 중 하나)"},
                "link": {"type": "STRING", "description": "프로그램 상세 정보 또는 신청 페이지 링크"},
            },
            "propertyOrdering": ["programName", "jobField", "location", "host", "status", "link"]
        }
    }

    try:
        # API 호출 구현 (Gemini 2.5 Flash를 사용하여 구조화된 응답 요청)
        api_key = "" # Canvas 환경에서 자동으로 제공됨
        api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-09-2025:generateContent?key={api_key}"
        
        payload = {
            "contents": [{"parts": [{"text": user_query}]}],
            "systemInstruction": {"parts": [{"text": system_prompt}]},
            "config": {
                "responseMimeType": "application/json",
                "responseSchema": response_schema
            }
        }
        
        # 실제 fetch는 Streamlit 환경에서 수행되며, 이 함수는 blocking 방식으로 실행됩니다.
        # 여기서는 Python stub을 사용하여 API 호출을 시뮬레이션하고,
        # 실제 환경에서는 Streamlit이 백엔드 HTTP 요청을 처리합니다.
        
        # ⚠️ 참고: Streamlit 환경에서는 이 Python 코드가 API를 직접 호출하는 것이 아니라,
        # 런타임에 백엔드 시스템이 이 `search_and_structure_programs` 함수를
        # 실행하고 결과를 반환합니다. 따라서 여기에 직접 `fetch`를 구현하는 대신
        # 논리적인 API 호출 흐름만 명시합니다.
        
        # Mock API Response for logic simulation
        # 실제 환경에서는 `response.json()`을 파싱하여 JSON 문자열을 얻어야 합니다.
        
        # 3. (실제 환경에서) API 응답 파싱
        # (이 부분은 Streamlit 컴포넌트 환경의 특성상 생략하고, 성공했다고 가정합니다.)
        
        # 예시: Mockup 결과 (실제로는 API에서 이 데이터를 받습니다)
        mock_data_if_no_api_call = [
            {"programName": "디지털 시대의 마케터 직업 체험", "jobField": "마케팅/광고", "location": "온라인", "host": "K-디지털 아카데미", "status": "모집 중", "link": "정보 없음"},
            {"programName": "친환경 도시 설계 워크숍", "jobField": "도시 계획/환경", "location": "부산", "host": "국토교통부", "status": "모집 마감", "link": "정보 없음"},
        ]
        
        # ⭐️ 개발 환경에서는 임시로 Mock 데이터를 반환합니다.
        # 실제 환경에서는 API를 통해 얻은 JSON 문자열을 `json.loads` 해야 합니다.
        return mock_data_if_no_api_call
    
    except Exception as e:
        st.error(f"데이터 구조화 중 오류 발생: {e}")
        return []


# --- 5. 페이지 렌더링 함수 ---

def render_login_page():
    """로그인 페이지를 Streamlit 네이티브 폼으로 렌더링합니다."""
    # (기존 로그인 로직 유지)
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
    # (기존 회원가입 로직 유지)
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
    """홈 화면을 렌더링합니다."""
    user_info = st.session_state.user_data
    user_name = user_info.get('studentName', '사용자')
    is_admin = user_info.get('isAdmin', False)

    st.title("🗺️ Job-Trekking 홈 💼")
    st.write(f"환영합니다, **{user_name}**님!")

    # 페이지 이동 버튼들 (Streamlit 네이티브 버튼)
    if st.button("📝 잡스리포트 기록하기", key="navigate_to_report"):
        navigate(PAGE_ADD_REPORT) 
        
    if st.button("📖 나의 기록 보기", key="navigate_to_view_reports"):
        navigate(PAGE_VIEW_REPORTS) 

    # ⭐️ 프로그램 목록 보기 버튼은 이제 검색 페이지로 연결됩니다. ⭐️
    if st.button("🔎 진로 프로그램 검색하기", key="navigate_to_program_list"):
        navigate(PAGE_PROGRAM_LIST)

    # ⭐️ 관리자 프로그램 추가 기능은 이제 제거되었습니다. ⭐️

    # home.html 파일 읽기
    html_content = read_html_file('home.html')
    
    if html_content:
        # 사용자 이름 등 동적 데이터를 HTML에 주입
        html_content = html_content.replace('{{USER_NAME}}', user_name)
        html_content = html_content.replace('{{USER_SCHOOL}}', user_info.get('schoolName', '학교 정보 없음'))
        html_content = html_content.replace('{{USER_CLASS}}', user_info.get('classNumber', '반 정보 없음'))
        
        components.html(
            html_content,
            height=300, 
            scrolling=False,
        )
    
    st.markdown("---")
    if st.button("로그아웃"):
        st.session_state.user_data = None
        navigate(PAGE_LOGIN)

def render_program_list_page():
    """
    ⭐️ 실시간 진로 프로그램 검색 및 목록 페이지 ⭐️
    """
    st.title("진로 프로그램 실시간 검색 🔎")
    st.info("프로그램명, 분야, 지역 등 원하는 키워드를 입력하면 최신 프로그램 정보를 찾아드립니다.")
    
    # 1. 검색 폼
    with st.form("program_search_form"):
        search_term = st.text_input("검색 키워드 입력", key="search_input", placeholder="예: AI 개발자 체험, 박물관 견학, 환경")
        search_submitted = st.form_submit_button("프로그램 검색")
        
    # 2. 검색 실행 및 결과 표시
    if search_submitted and search_term:
        
        # ⭐️ 검색 및 구조화 함수 호출 ⭐️
        # st.cache_data 덕분에 로딩 스피너와 캐싱이 자동으로 적용됩니다.
        st.session_state.search_results = search_and_structure_programs(search_term)
        
        if not st.session_state.search_results:
            st.warning(f"'{search_term}'에 대한 검색 결과를 찾을 수 없거나 구조화에 실패했습니다. 다른 키워드로 시도해 주세요.")
        
    # 3. 검색 결과 목록 표시
    programs = st.session_state.search_results

    if programs:
        st.markdown("---")
        st.subheader(f"총 {len(programs)}개의 검색 결과를 찾았습니다.")
        
        for program in programs:
            # ⭐️ 필요한 6가지 항목을 깔끔하게 정리하여 표시 ⭐️
            program_name = program.get('programName', '제목 없음')
            job_field = program.get('jobField', '정보 없음')
            status = program.get('status', '미정')
            host = program.get('host', '정보 없음')
            location = program.get('location', '정보 없음')
            link = program.get('link', '정보 없음')
            
            with st.expander(f"**[{status}]** {program_name} ({job_field})", expanded=True):
                st.markdown(f"**관련 분야:** `{job_field}`")
                st.markdown(f"**장소:** `{location}`")
                st.markdown(f"**운영 기관:** `{host}`")
                if link != '정보 없음' and link.startswith('http'):
                    st.markdown(f"**참고 링크:** [자세히 보기]({link})")
                else:
                    st.markdown(f"**참고 링크:** {link}")


    st.markdown("---")
    if st.button("메인 화면으로 돌아가기", key="back_to_home_from_list"):
        navigate(PAGE_HOME)

# ⭐️ render_add_program_page는 사용하지 않습니다. ⭐️
# 기존 코드를 제거하고, 사용자가 요청한 새로운 흐름에 집중합니다.

def render_add_report_page():
    """
    HTML 컴포넌트로 폼 입력만 표시하고, Streamlit 네이티브 버튼으로 저장 처리를 수행합니다.
    """
    st.title("잡스리포트 기록하기 📝")
    
    # 1. HTML 컴포넌트 렌더링 (폼 입력만 담당)
    add_report_html = read_html_file('add_report.html')
    
    component_value = None
    
    html_content_safe = str(add_report_html) if add_report_html is not None else ""

    if html_content_safe.strip():
        try:
            component_value = components.html(
                html=html_content_safe,
                height=700, 
                scrolling=True
            )
        except Exception as e:
            st.error(f"⚠️ 컴포넌트 렌더링 중 Streamlit 내부 오류 발생: {e}. HTML 파일 내용을 다시 확인해 주세요.")


    # 2. HTML 컴포넌트로부터 전달받은 데이터 추출 및 상태 업데이트
    if isinstance(component_value, dict) and 'reportData' in component_value:
        current_data = component_value['reportData']
        st.session_state.current_report_data = current_data if current_data is not None else {}
    
    
    st.markdown("---")

    # 3. Streamlit 네이티브 버튼 (저장 로직 트리거)
    if st.button("🚀 리포트 저장하기", key="submit_report_button"):
        
        data_to_save = st.session_state.get('current_report_data', {}) 

        # ⭐️ 강화된 유효성 검사 ⭐️
        is_valid = (
            data_to_save.get('programName', '').strip() != '' and 
            data_to_save.get('experienceDate') and 
            data_to_save.get('rating') is not None and 
            data_to_save.get('reportContent', '').strip() != ''
        )

        if is_valid:
            
            success, message = save_report_to_firestore(data_to_save)
            
            if success:
                st.session_state.report_saved_successfully = True
                st.session_state.current_report_data = {} 
                st.rerun() 
            else:
                st.error(f"⚠️ 리포트 저장 실패: {message}")
        else:
            st.error("⚠️ 폼 데이터가 준비되지 않았습니다. 모든 필수 항목(프로그램명, 일자, 별점, 소감)을 입력했는지 확인해 주세요.")
            
            missing_fields = []
            if data_to_save.get('programName', '').strip() == '':
                missing_fields.append("체험 프로그램명")
            if not data_to_save.get('experienceDate'):
                missing_fields.append("체험 일자")
            if data_to_save.get('rating') is None:
                missing_fields.append("별점")
            if data_to_save.get('reportContent', '').strip() == '':
                missing_fields.append("소감 및 기록 내용")

            if missing_fields:
                 st.warning(f"❌ **누락된 필수 항목:** {', '.join(missing_fields)}를 모두 입력해야 저장할 수 있습니다.")


    # 4. 저장 성공 후 상태 
    if st.session_state.get('report_saved_successfully', False):
        st.success("🎉 리포트가 성공적으로 저장되었습니다. 다음 활동을 선택해 주세요.")
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
    """
    # (기존 잡스리포트 목록 보기 로직 유지)
    st.title("나의 진로 체험 기록 📖")
    st.info("이 페이지에서는 지금까지 작성한 잡스리포트 목록을 볼 수 있습니다. (개인 기록)")
    
    user_id = get_current_user_id()
    if not user_id:
        st.error("사용자 인증 정보를 찾을 수 없습니다. 로그인 상태를 확인해 주세요.")
        return

    all_reports = st.session_state.firestore_reports.get(user_id, [])
    
    if not all_reports:
        st.markdown(
            "<div style='text-align: center; padding: 20px; background-color: #f0f0f5; border-radius: 8px;'>"
            "<strong>작성된 리포트가 없습니다.</strong><br>지금 바로 '잡스리포트 기록하기'를 통해 기록을 시작해 보세요!"
            "</div>", unsafe_allow_html=True
        )
        
    else:
        sorted_reports = sorted(all_reports, key=lambda x: x['createdAt'], reverse=True)
        
        st.sidebar.header("리포트 목록")
        st.sidebar.markdown(f"총 **{len(sorted_reports)}**건의 기록이 있습니다.")

        report_titles = [f"{r['experienceDate']} - {r['programName']}" for r in sorted_reports]
        
        if report_titles:
            selected_title = st.sidebar.selectbox("리포트 선택", report_titles)

            selected_report_index = report_titles.index(selected_title)
            selected_report = sorted_reports[selected_report_index]

            def get_rating_stars(rating):
                rating = max(0, min(5, rating))
                return "★" * rating + "☆" * (5 - rating)

            st.markdown("---")
            st.subheader(f"✅ {selected_report['programName']}")
            
            col_date, col_field = st.columns(2)
            with col_date:
                st.markdown(f"**체험 일자:** `{selected_report['experienceDate']}`")
            with col_field:
                # jobField가 필수 입력 항목이 아니었을 수 있으므로 안전하게 처리
                st.markdown(f"**분야:** `{selected_report.get('jobField', '미입력') or '미입력'}`") 

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


# --- 6. 메인 렌더링 루프 ---

current_user_authenticated = (st.session_state.user_data is not None)

if st.session_state.current_page == PAGE_LOGIN:
    render_login_page()
elif st.session_state.current_page == PAGE_SIGNUP:
    render_signup_page()
elif st.session_state.current_page == PAGE_HOME and current_user_authenticated:
    render_home_page()
elif st.session_state.current_page == PAGE_PROGRAM_LIST and current_user_authenticated:
    render_program_list_page()
elif st.session_state.current_page == PAGE_ADD_REPORT and current_user_authenticated:
    render_add_report_page()
elif st.session_state.current_page == PAGE_VIEW_REPORTS and current_user_authenticated:
    render_view_reports_page()
else:
    st.session_state.current_page = PAGE_LOGIN
    navigate(PAGE_LOGIN)

st.sidebar.markdown(f"**현재 로드 중인 페이지:** {st.session_state.current_page.upper()}")
