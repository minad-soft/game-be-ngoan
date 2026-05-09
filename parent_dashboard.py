import streamlit as st
import db_helper
from datetime import datetime, timedelta

def render_parent_dashboard():
    st.title("⚙️ Trạm Kiểm Soát Của Ba Mẹ")
    
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "Duyệt Nhiệm Vụ", "Nhiệm Vụ", "📅 Lịch Tuần", "📊 Báo Cáo", "Kho Quà Tặng", "Cấu Hình"
    ])
    
    # ==================== TAB 1: DUYỆT NHIỆM VỤ ====================
    with tab1:
        st.header("⏳ Nhiệm Vụ Chờ Duyệt")
        pending = db_helper.get_pending_approvals()
        tasks = db_helper.get_tasks()
        
        if not pending:
            st.info("Không có nhiệm vụ nào đang chờ duyệt.")
        else:
            for log_id, log_data in list(pending.items()):
                task_id = log_data.get('task_id')
                task_data = tasks.get(task_id, {})
                
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    st.write(f"**{task_data.get('title', 'Không rõ')}**")
                    st.caption(f"Yêu cầu lúc: {log_data.get('timestamp')}")
                with col2:
                    if st.button("✅ Duyệt", key=f"approve_{log_id}"):
                        db_helper.approve_task(log_id, task_id, task_data.get('stars_reward', 0))
                        st.success("Đã duyệt!")
                        st.rerun()
                with col3:
                    if st.button("❌ Từ chối", key=f"reject_{log_id}"):
                        db_helper.reject_task(log_id)
                        st.warning("Đã từ chối.")
                        st.rerun()
                st.markdown("---")
                
    # ==================== TAB 2: QUẢN LÝ NHIỆM VỤ ====================
    with tab2:
        st.header("📝 Quản Lý Nhiệm Vụ")
        tasks = db_helper.get_tasks()
        
        # State cho việc sửa nhiệm vụ
        if 'editing_task_id' not in st.session_state:
            st.session_state['editing_task_id'] = None
        
        editing_id = st.session_state['editing_task_id']
        editing_data = tasks.get(editing_id, {}) if editing_id else {}
        
        # Form thêm / sửa nhiệm vụ
        form_title = f"✏️ Đang sửa: {editing_data.get('title')}" if editing_id else "➕ Thêm Nhiệm Vụ Mới"
        with st.expander(form_title, expanded=bool(editing_id)):
            with st.form("form_add_task", clear_on_submit=True):
                t_title = st.text_input("Tên nhiệm vụ", value=editing_data.get('title', ''), autocomplete="off")
                t_icon = st.text_input("Icon (Emoji)", value=editing_data.get('icon', '📝'), autocomplete="off")
                t_stars = st.number_input("Số sao thưởng", min_value=1, value=int(editing_data.get('stars_reward', 5)))
                t_req_approval = st.checkbox("Cần ba mẹ duyệt?", value=editing_data.get('requires_approval', False))
                
                col_save, col_cancel = st.columns(2)
                with col_save:
                    btn_label = "💾 Lưu thay đổi" if editing_id else "Thêm nhiệm vụ"
                    if st.form_submit_button(btn_label):
                        if t_title:
                            db_helper.save_task(editing_id, t_title, t_icon, t_stars, t_req_approval)
                            st.success("Đã lưu!" if editing_id else "Đã thêm nhiệm vụ!")
                            st.session_state['editing_task_id'] = None
                            st.rerun()
                        else:
                            st.error("Vui lòng nhập tên nhiệm vụ.")
                with col_cancel:
                    if editing_id:
                        if st.form_submit_button("❌ Hủy sửa"):
                            st.session_state['editing_task_id'] = None
                            st.rerun()
        
        # List existing tasks
        st.subheader("Danh sách hiện tại")
        if tasks:
            for t_id, t_data in tasks.items():
                col1, col2, col3 = st.columns([4, 1, 1])
                with col1:
                    approval_tag = "🔒 Cần duyệt" if t_data.get('requires_approval') else "⚡ Tự động"
                    st.write(f"{t_data.get('icon')} **{t_data.get('title')}** — {t_data.get('stars_reward')} ⭐ `{approval_tag}`")
                with col2:
                    if st.button("✏️ Sửa", key=f"edit_task_{t_id}"):
                        st.session_state['editing_task_id'] = t_id
                        st.rerun()
                with col3:
                    if st.button("🗑️ Xóa", key=f"del_task_{t_id}"):
                        db_helper.delete_task(t_id)
                        if st.session_state.get('editing_task_id') == t_id:
                            st.session_state['editing_task_id'] = None
                        st.rerun()
        else:
            st.write("Chưa có nhiệm vụ nào.")

    # ==================== TAB 3: LỊCH TUẦN ====================
    with tab3:
        st.header("📅 Thời Khóa Biểu Tuần")
        st.caption("Chọn những nhiệm vụ mặc định cho bé trong từng ngày. Bé chỉ thấy các nhiệm vụ được gán cho ngày hôm đó.")
        
        tasks = db_helper.get_tasks()
        schedule = db_helper.get_weekly_schedule()
        
        if not tasks:
            st.warning("Chưa có nhiệm vụ nào. Hãy tạo nhiệm vụ ở tab **Nhiệm Vụ** trước.")
        else:
            task_ids = list(tasks.keys())
            task_labels = {tid: f"{tasks[tid].get('icon')} {tasks[tid].get('title')}" for tid in task_ids}
            
            new_schedule = {}
            
            for day_key in db_helper.DAYS_OF_WEEK:
                day_vi = db_helper.DAYS_VI[day_key]
                current_ids = schedule.get(day_key, [])
                # Lọc bỏ task_id không còn tồn tại
                current_ids = [tid for tid in current_ids if tid in tasks]
                
                selected = st.multiselect(
                    f"**{day_vi}**",
                    options=task_ids,
                    default=current_ids,
                    format_func=lambda tid: task_labels.get(tid, tid),
                    key=f"sched_{day_key}"
                )
                new_schedule[day_key] = selected
            
            if st.button("💾 Lưu Thời Khóa Biểu", use_container_width=True):
                db_helper.save_weekly_schedule(new_schedule)
                st.success("Đã lưu thời khóa biểu tuần!")
                st.rerun()

    # ==================== TAB 4: BÁO CÁO ====================
    with tab4:
        st.header("📊 Báo Cáo Hoạt Động")
        
        tasks = db_helper.get_tasks()
        kid = db_helper.get_kid_profile()
        
        # Chọn tuần để xem
        today = datetime.now().date()
        # Tính ngày đầu tuần (Thứ Hai)
        start_of_week = today - timedelta(days=today.weekday())
        
        col_nav1, col_nav2, col_nav3 = st.columns([1, 2, 1])
        
        if 'report_week_offset' not in st.session_state:
            st.session_state['report_week_offset'] = 0
        
        with col_nav1:
            if st.button("◀️ Tuần trước"):
                st.session_state['report_week_offset'] -= 1
                st.rerun()
        with col_nav3:
            if st.button("Tuần sau ▶️"):
                st.session_state['report_week_offset'] += 1
                st.rerun()
        
        offset = st.session_state['report_week_offset']
        view_start = start_of_week + timedelta(weeks=offset)
        view_end = view_start + timedelta(days=6)
        
        with col_nav2:
            st.markdown(f"### 📆 {view_start.strftime('%d/%m')} — {view_end.strftime('%d/%m/%Y')}")
        
        # Lấy báo cáo
        report = db_helper.get_weekly_report(view_start)
        
        # Hiển thị dạng bảng lịch
        st.subheader("📋 Lịch Hoạt Động")
        
        total_done_week = 0
        total_scheduled_week = 0
        
        for date_str, day_data in report.items():
            day_vi = day_data['day_vi']
            done = day_data['done_count']
            total = day_data['total_count']
            rate = day_data['rate']
            is_today = (date_str == today.strftime('%Y-%m-%d'))
            
            total_done_week += done
            total_scheduled_week += total
            
            # Đánh giá theo ngày
            if total == 0:
                eval_icon = "⬜"
                eval_text = "Không có nhiệm vụ"
            elif rate == 100:
                eval_icon = "🌟"
                eval_text = "Xuất sắc!"
            elif rate >= 70:
                eval_icon = "👍"
                eval_text = "Tốt lắm!"
            elif rate >= 40:
                eval_icon = "💪"
                eval_text = "Cố thêm nhé!"
            else:
                eval_icon = "😢"
                eval_text = "Cần cải thiện"
            
            # Highlight hôm nay
            day_label = f"**🔵 {day_vi} ({date_str}) — HÔM NAY**" if is_today else f"**{day_vi} ({date_str})**"
            
            with st.expander(f"{eval_icon} {day_label} — {done}/{total} nhiệm vụ ({rate}%)"):
                if total == 0 and done == 0:
                    st.caption("Chưa có dữ liệu cho ngày này.")
                else:
                    # Chi tiết task đã hoàn thành
                    scheduled_ids = day_data['scheduled']
                    completed_ids = day_data['completed']
                    
                    if scheduled_ids:
                        for tid in scheduled_ids:
                            t = tasks.get(tid, {})
                            if tid in completed_ids:
                                st.write(f"✅ ~~{t.get('icon','')} {t.get('title','')}~~ — +{t.get('stars_reward',0)} ⭐")
                            else:
                                st.write(f"❌ {t.get('icon','')} {t.get('title','')} — chưa hoàn thành")
                    else:
                        for tid in completed_ids:
                            t = tasks.get(tid, {})
                            if t:
                                st.write(f"✅ {t.get('icon','')} {t.get('title','')} — +{t.get('stars_reward',0)} ⭐")
                    
                    st.info(f"Đánh giá: {eval_icon} {eval_text}")
        
        # Đánh giá tổng kết tuần
        st.divider()
        st.subheader("🏆 Tổng Kết Tuần")
        
        week_rate = (total_done_week / total_scheduled_week * 100) if total_scheduled_week > 0 else 0
        
        col_m1, col_m2, col_m3 = st.columns(3)
        with col_m1:
            st.metric("Đã hoàn thành", f"{total_done_week}/{total_scheduled_week}")
        with col_m2:
            st.metric("Tỷ lệ", f"{round(week_rate, 1)}%")
        with col_m3:
            if week_rate >= 90:
                st.metric("Đánh giá", "🌟 Xuất sắc!")
            elif week_rate >= 70:
                st.metric("Đánh giá", "👍 Tốt lắm!")
            elif week_rate >= 40:
                st.metric("Đánh giá", "💪 Khá tốt")
            elif total_scheduled_week == 0:
                st.metric("Đánh giá", "⬜ Chưa có dữ liệu")
            else:
                st.metric("Đánh giá", "📈 Cần cố gắng")
        
        # Progress bar
        st.progress(min(week_rate / 100, 1.0))

    # ==================== TAB 5: KHO QUÀ ====================
    with tab5:
        st.header("🎁 Quản Lý Kho Quà")
        rewards = db_helper.get_rewards_pool()
        
        # Add new reward form
        with st.expander("➕ Thêm Quà Tặng Mới"):
            with st.form("form_add_reward"):
                r_name = st.text_input("Tên món quà", autocomplete="off")
                r_icon = st.text_input("Icon (Emoji hoặc URL)", value="🎁", autocomplete="off")
                r_prob = st.number_input("Tỷ lệ trúng (%)", min_value=1, max_value=100, value=10)
                if st.form_submit_button("Thêm quà"):
                    if r_name:
                        db_helper.save_reward(None, r_name, r_prob, r_icon)
                        st.success("Đã thêm phần thưởng!")
                        st.rerun()
        
        # List existing rewards
        st.subheader("Danh sách quà tặng")
        if rewards:
            for r_id, r_data in rewards.items():
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.write(f"{r_data.get('icon_url')} **{r_data.get('name')}** - Tỷ lệ: {r_data.get('probability')}%")
                with col2:
                    if st.button("🗑️ Xóa", key=f"del_rew_{r_id}"):
                        db_helper.delete_reward(r_id)
                        st.rerun()
        else:
            st.write("Kho quà đang trống.")
        
    # ==================== TAB 6: CẤU HÌNH ====================
    with tab6:
        st.header("⚙️ Cấu Hình Hệ Thống")
        config = db_helper.get_system_config()
        kid_profile = db_helper.get_kid_profile()
        
        new_name = st.text_input("Tên của bé", value=kid_profile.get('name', 'Bảo Nam'), autocomplete="off")
        if st.button("Lưu tên"):
            db_helper.update_kid_name(new_name)
            st.success("Đã cập nhật tên của bé!")
            
        st.markdown("---")
        
        new_pin = st.text_input("Mã PIN", value=config.get('parent_pin', '1234'), type="password", autocomplete="one-time-code")
        if st.button("Lưu PIN"):
            db_helper.update_system_config('parent_pin', new_pin)
            st.success("Đã cập nhật mã PIN!")
            
        st.markdown("---")
        
        new_stars = st.number_input("Số sao cần để mở túi mù", value=int(config.get('stars_required_for_blindbag', 50)), min_value=1)
        if st.button("Lưu số sao"):
            db_helper.update_system_config('stars_required_for_blindbag', new_stars)
            st.success("Đã cập nhật!")
            
    st.divider()
    if st.button("🔙 Khóa Trạm & Trở Về"):
        st.session_state['parent_mode_authenticated'] = False
        st.rerun()
