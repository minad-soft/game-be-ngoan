import streamlit as st
import db_helper
from kid_dashboard import render_kid_dashboard
from parent_dashboard import render_parent_dashboard

st.set_page_config(page_title="Game Bé Ngoan", page_icon="🚀", layout="centered")

# Load CSS
try:
    with open("style.css", "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except FileNotFoundError:
    pass

# Initialize Session State
if 'parent_mode_authenticated' not in st.session_state:
    st.session_state['parent_mode_authenticated'] = False
if 'show_parent_login' not in st.session_state:
    st.session_state['show_parent_login'] = False

# Sidebar for Parent Gatekeeper
with st.sidebar:
    st.title("👨‍👩‍👧 Khu Vực Phụ Huynh")
    if not st.session_state['parent_mode_authenticated']:
        if not st.session_state['show_parent_login']:
            if st.button("⚙️ Cài đặt & Duyệt bài", use_container_width=True):
                st.session_state['show_parent_login'] = True
                st.rerun()
                
        if st.session_state['show_parent_login']:
            with st.form("form_login"):
                st.info("Khu vực bảo mật")
                pin_input = st.text_input("Nhập mã PIN", type="password", autocomplete="one-time-code")
                col1, col2 = st.columns(2)
                with col1:
                    submitted = st.form_submit_button("Xác nhận", use_container_width=True)
                with col2:
                    cancel = st.form_submit_button("Hủy", use_container_width=True)
                
            if submitted:
                config = db_helper.get_system_config()
                if pin_input == config.get('parent_pin', '1234'):
                    st.session_state['parent_mode_authenticated'] = True
                    st.session_state['show_parent_login'] = False
                    st.success("Thành công!")
                    st.rerun()
                else:
                    st.error("PIN sai!")
            if cancel:
                st.session_state['show_parent_login'] = False
                st.rerun()
    else:
        st.success("Đang ở chế độ Phụ huynh")
        if st.button("🔙 Quay lại màn hình của bé", use_container_width=True):
            st.session_state['parent_mode_authenticated'] = False
            st.rerun()

# Main Routing
if st.session_state.get('parent_mode_authenticated'):
    render_parent_dashboard()
else:
    render_kid_dashboard()
