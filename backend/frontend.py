# frontend.py

import streamlit as st
import requests
import pandas as pd
import os
import logging
from datetime import date

# --- 백엔드 URL 설정 ---
# 쿠버네티스 환경 변수 또는 로컬 .env 파일에서 URL을 가져옵니다.
BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:5050")

# --- 로깅 설정 ---
log = logging.getLogger("frontend")
if not log.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    log.addHandler(handler)
log.setLevel(logging.INFO)

# --- 페이지 기본 설정 ---
st.set_page_config(page_title="TrackFit", page_icon="💨", layout="wide")
st.title("TrackFit - 러닝 기록 서비스")


# --- 1. 로그인/회원가입 화면 ---
if 'token' not in st.session_state:
    
    login_tab, signup_tab = st.tabs(["로그인", "회원가입"])

    # --- 로그인 탭 ---
    with login_tab:
        st.subheader("로그인")
        with st.form("login_form"):
            email = st.text_input("이메일")
            password = st.text_input("비밀번호", type="password")
            login_submitted = st.form_submit_button("로그인")

            if login_submitted:
                try:
                    response = requests.post(
                        f"{BACKEND_URL}/api/v1/auth/login",
                        data={"username": email, "password": password}
                    )
                    if response.status_code == 200:
                        st.session_state['token'] = response.json()['access_token']
                        st.session_state['user_email'] = email
                        st.rerun()
                    else:
                        st.error("이메일 또는 비밀번호가 잘못되었습니다.")
                except requests.exceptions.RequestException as e:
                    st.error(f"서버에 연결할 수 없습니다: {e}")

    # --- 회원가입 탭 ---
    with signup_tab:
        st.subheader("새로운 계정 만들기")
        with st.form("signup_form"):
            username = st.text_input("사용자 이름")
            new_email = st.text_input("이메일 주소")
            new_password = st.text_input("새 비밀번호", type="password")
            signup_submitted = st.form_submit_button("가입하기")

            if signup_submitted:
                try:
                    response = requests.post(
                        f"{BACKEND_URL}/api/v1/auth/signup",
                        json={"username": username, "email": new_email, "password": new_password}
                    )
                    if response.status_code == 200:
                        st.success("회원가입이 완료되었습니다! 로그인 탭에서 로그인해주세요.")
                    elif response.status_code == 400:
                        st.error("이미 사용 중인 이메일입니다.")
                    else:
                        st.error(f"회원가입 중 오류가 발생했습니다: {response.text}")
                except requests.exceptions.RequestException as e:
                    st.error(f"서버에 연결할 수 없습니다: {e}")


# --- 2. 로그인 후 메인 화면 ---
else:
    # --- 사이드바 ---
    st.sidebar.success(f"{st.session_state['user_email']}님, 환영합니다.")
    if st.sidebar.button("로그아웃"):
        del st.session_state['token']
        del st.session_state['user_email']
        st.rerun()

    headers = {"Authorization": f"Bearer {st.session_state['token']}"}

    col1, col2 = st.columns(2)

    # --- 왼쪽 컬럼: 기록 추가 및 리포트 요청 ---
    with col1:
        # --- 달리기 기록 추가 ---
        with st.expander("새로운 달리기 기록 추가", expanded=True):
            with st.form("run_form", clear_on_submit=True):
                distance_km = st.number_input("거리 (km)", min_value=0.1, step=0.1, format="%.2f")
                duration_seconds = st.number_input("시간 (초)", min_value=1)
                notes = st.text_area("메모")
                run_submitted = st.form_submit_button("기록 추가")

                if run_submitted:
                    try:
                        response = requests.post(
                            f"{BACKEND_URL}/api/v1/runs/", headers=headers,
                            json={"distance_km": distance_km, "duration_seconds": duration_seconds, "notes": notes}
                        )
                        if response.status_code == 201:
                            st.success("달리기 기록이 성공적으로 추가되었습니다!")
                        else:
                            st.error(f"기록 추가에 실패했습니다: {response.text}")
                    except requests.exceptions.RequestException as e:
                        st.error(f"서버에 연결할 수 없습니다: {e}")

        # --- 리포트 생성 요청 ---
        with st.expander("데일리 리포트 생성 요청"):
            with st.form("report_form", clear_on_submit=True):
                target_date = st.date_input("분석할 날짜 선택", value=date.today())
                report_submitted = st.form_submit_button("리포트 요청")

                if report_submitted:
                    try:
                        payload = {"report_type": "daily", "target_date": target_date.isoformat()}
                        log.info(f"Sending report creation request: payload={payload}")
                        response = requests.post(
                            f"{BACKEND_URL}/api/v1/reports/", headers=headers, json=payload
                        )
                        log.info(f"Report creation response: status_code={response.status_code}")
                        if response.status_code == 202:
                            st.success(f"{target_date}의 리포트 생성이 요청되었습니다. 잠시 후 백그라운드에서 처리됩니다.")
                        else:
                            log.error(f"Report creation failed: status_code={response.status_code}, body={response.text}")
                            st.error(f"리포트 요청에 실패했습니다: {response.text}")
                    except requests.exceptions.RequestException as e:
                        log.error(f"Report creation request error: {e}")
                        st.error(f"서버에 연결할 수 없습니다: {e}")

    # --- 오른쪽 컬럼: 기록 및 리포트 조회 ---
    with col2:
        # --- 달리기 기록 조회 ---
        st.subheader("나의 달리기 기록")
        if st.button("기록 새로고침"):
            try:
                response = requests.get(f"{BACKEND_URL}/api/v1/runs/", headers=headers)
                if response.status_code == 200:
                    runs = response.json()
                    if runs:
                        df_runs = pd.DataFrame(runs).sort_values(by="run_date", ascending=False)
                        st.dataframe(df_runs[['run_date', 'distance_km', 'duration_seconds', 'notes']])
                    else:
                        st.info("아직 달리기 기록이 없습니다.")
                else:
                    st.error("기록을 불러오는 데 실패했습니다.")
            except requests.exceptions.RequestException as e:
                st.error(f"서버에 연결할 수 없습니다: {e}")

        # --- 👇 [추가된 부분] 리포트 목록 조회 ---
        st.subheader("나의 리포트")
        if st.button("리포트 목록 새로고침"):
            try:
                # GET /api/v1/reports/ API가 백엔드에 구현되어 있어야 합니다.
                response = requests.get(f"{BACKEND_URL}/api/v1/reports/", headers=headers)
                if response.status_code == 200:
                    reports = response.json()
                    if reports:
                        df_reports = pd.DataFrame(reports).sort_values(by="target_date", ascending=False)
                        st.dataframe(df_reports[['target_date', 'report_type', 'status']])
                        
                        # 완료된 리포트가 있으면 내용 보여주기
                        completed_reports = [r for r in reports if r['status'] == 'COMPLETED' and r['content']]
                        if completed_reports:
                            st.write("---")
                            st.write("#### 리포트 목록")
                            for report in completed_reports:
                                st.json(report['content'])
                    else:
                        st.info("아직 생성된 리포트가 없습니다.")
                else:
                    st.error("리포트 목록을 불러오는 데 실패했습니다.")
            except requests.exceptions.RequestException as e:
                st.error(f"서버에 연결할 수 없습니다: {e}")

