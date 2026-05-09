import streamlit as st
import db_helper
import game_logic
import time
import requests
from streamlit_lottie import st_lottie

def load_lottieurl(url: str):
    try:
        r = requests.get(url)
        if r.status_code != 200:
            return None
        return r.json()
    except:
        return None

def play_sound(sound_url: str):
    """Phát âm thanh tự động bằng HTML tag"""
    audio_html = f'''
        <audio autoplay="true" style="display:none;">
            <source src="{sound_url}" type="audio/mp3">
        </audio>
    '''
    st.markdown(audio_html, unsafe_allow_html=True)

def render_kid_dashboard():
    st.title("🚀 Trạm Không Gian Của Bé")
    
    # Load kid profile
    kid = db_helper.get_kid_profile()
    config = db_helper.get_system_config()
    required_stars = config.get('stars_required_for_blindbag', 50)
    
    col1, col2 = st.columns([2, 1])
    with col1:
        st.subheader(f"Xin chào phi hành gia, {kid.get('name', 'Bé')}! 🧑‍🚀")
    with col2:
        st.metric(label="⭐ Sao của bé", value=kid.get('total_stars', 0))
        
    st.divider()
    
    # Tasks Section - Chỉ hiển thị nhiệm vụ hôm nay theo lịch tuần
    today_key = db_helper.get_today_day_key()
    today_vi = db_helper.DAYS_VI.get(today_key, today_key)
    st.header(f"📋 Nhiệm vụ {today_vi}")
    tasks = db_helper.get_tasks_for_today()
    
    if not tasks:
        st.info("Hôm nay không có nhiệm vụ nào. Hãy nghỉ ngơi nhé! 🎉")
    
    cols = st.columns(2)
    for idx, (task_id, task_data) in enumerate(tasks.items()):
        with cols[idx % 2]:
            completed = db_helper.is_task_completed_today(task_id)
            pending = db_helper.is_task_pending_approval(task_id)
            
            if completed:
                st.markdown(f"### ✅ ~~{task_data.get('icon', '📝')} {task_data.get('title', 'Nhiệm vụ')}~~")
                st.success(f"Đã hoàn thành! +{task_data.get('stars_reward', 0)} ⭐")
            elif pending:
                st.markdown(f"### ⏳ {task_data.get('icon', '📝')} {task_data.get('title', 'Nhiệm vụ')}")
                st.warning("Đang chờ ba mẹ duyệt...")
            else:
                st.markdown(f"### {task_data.get('icon', '📝')} {task_data.get('title', 'Nhiệm vụ')}")
                st.write(f"Phần thưởng: **{task_data.get('stars_reward', 0)} ⭐**")
                
                if st.button(f"Hoàn thành", key=f"btn_{task_id}"):
                    if task_data.get('requires_approval'):
                        db_helper.add_pending_approval(task_id)
                        st.success("Đã gửi cho ba mẹ duyệt! ⏳")
                        st.rerun()
                    else:
                        new_stars = db_helper.update_kid_stars(task_data.get('stars_reward', 0))
                        db_helper.mark_task_completed(task_id)
                        play_sound("https://assets.mixkit.co/active_storage/sfx/2013/2013-preview.mp3")
                        st.success(f"Tuyệt vời! Bé được cộng {task_data.get('stars_reward', 0)} ⭐")
                        st.balloons()
                        time.sleep(1.5)
                        st.rerun()
            st.markdown("---")

    st.divider()
    
    # Gacha Section (Blindbag)
    st.header("🎁 Mở Túi Mù Phi Thuyền")
    st.write(f"Cần **{required_stars} ⭐** để mở 1 túi mù.")
    
    current_stars = db_helper.get_kid_profile().get('total_stars', 0)
    
    if current_stars >= required_stars:
        if st.button("🚀 MỞ PHI THUYỀN NGAY 🚀", use_container_width=True):
            with st.spinner("Đang mở túi mù..."):
                # Deduct stars
                success, new_stars = db_helper.deduct_kid_stars(required_stars)
                if success:
                    # Animation
                    # Using a placeholder URL for rocket, you can replace with a valid lottie json
                    lottie_rocket = load_lottieurl("https://assets9.lottiefiles.com/packages/lf20_t2wjd250.json") 
                    if lottie_rocket:
                        st_lottie(lottie_rocket, height=200, key="rocket")
                    
                    play_sound("https://assets.mixkit.co/active_storage/sfx/1435/1435-preview.mp3") # Âm thanh mở quà / Tada
                    time.sleep(2)
                    
                    # Get reward
                    reward = game_logic.spin_gacha()
                    if reward:
                        st.snow()
                        st.success(f"🎉 Chúc mừng bé nhận được: {reward.get('name')} {reward.get('icon_url')}!")
                    else:
                        st.error("Rất tiếc, kho quà đang trống. Hãy nhờ ba mẹ nạp thêm quà nhé!")
                else:
                    st.error("Không đủ sao rồi!")
            if st.button("Đóng lại"):
                st.rerun()
    else:
        st.info(f"Bé cần thêm {required_stars - current_stars} ⭐ nữa để mở túi mù. Cố lên nhé!")
