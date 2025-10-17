# frontend.py

import streamlit as st
import requests
import pandas as pd
import os
from dotenv import load_dotenv

BACKEND_URL = os.getenv("BACKEND_URL")

st.set_page_config(page_title="TrackFit", page_icon="💨", layout="wide")
st.title("TrackFit - 러닝 기록")


if 'token' not in st.session_state:
    st.subheader("로그인")
    
    with st.form("login_form"):
        email = st.text_input("이메일")
        password = st.text_input("비밀번호", type="password")
        submitted = st.form_submit_button("로그인")

        if submitted:
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

else:
    st.sidebar.success(f"{st.session_state['user_email']}님, 환영합니다.")
    if st.sidebar.button("로그아웃"):
        del st.session_state['token']
        del st.session_state['user_email']
        st.rerun()

    st.subheader("새로운 달리기 기록 추가")
    with st.form("run_form", clear_on_submit=True):
        distance_km = st.number_input("거리 (km)", min_value=0.1, step=0.1, format="%.2f")
        duration_seconds = st.number_input("시간 (초)", min_value=1)
        notes = st.text_area("메모")
        submitted = st.form_submit_button("기록 추가")

        if submitted:
            headers = {"Authorization": f"Bearer {st.session_state['token']}"}
            data = {
                "distance_km": distance_km,
                "duration_seconds": duration_seconds,
                "notes": notes
            }
            response = requests.post(f"{BACKEND_URL}/api/v1/runs/", headers=headers, json=data)
            
            if response.status_code == 201:
                st.success("달리기 기록이 성공적으로 추가되었습니다!")
            else:
                st.error("기록 추가에 실패했습니다.")

    st.subheader("나의 달리기 기록")
    if st.button("새로고침"):
        headers = {"Authorization": f"Bearer {st.session_state['token']}"}
        response = requests.get(f"{BACKEND_URL}/api/v1/runs/", headers=headers)
        
        if response.status_code == 200:
            runs = response.json()
            if runs:
                df = pd.DataFrame(runs).sort_values(by="run_date", ascending=False)
                st.dataframe(df)
            else:
                st.info("아직 달리기 기록이 없습니다.")
        else:
            st.error("기록을 불러오는 데 실패했습니다.")