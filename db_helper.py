import json
import os
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, db
import streamlit as st

DB_URL = 'https://game-be-ngoan-default-rtdb.asia-southeast1.firebasedatabase.app/'
KEY_FILE = 'firebase_key.json'

# Khởi tạo Firebase App (Chỉ gọi 1 lần trong Streamlit)
if not firebase_admin._apps:
    try:
        # Nếu có cài biến môi trường FIREBASE_JSON trên Streamlit Cloud
        if "FIREBASE_JSON" in st.secrets:
            cred_dict = json.loads(st.secrets["FIREBASE_JSON"])
            cred = credentials.Certificate(cred_dict)
        else:
            # Nếu chạy trên máy tính cá nhân thì đọc file
            cred = credentials.Certificate(KEY_FILE)
            
        firebase_admin.initialize_app(cred, {
            'databaseURL': DB_URL
        })
    except Exception as e:
        print("Lỗi khởi tạo Firebase:", e)

def load_db():
    try:
        ref = db.reference('/')
        data = ref.get()
        if data is None:
            return {}
        return data
    except Exception as e:
        print("Lỗi đọc Firebase:", e)
        return {}

def save_db(data):
    try:
        ref = db.reference('/')
        ref.set(data)
    except Exception as e:
        print("Lỗi ghi Firebase:", e)

def get_kid_profile():
    data = load_db()
    return data.get('users', {}).get('kid_profile', {})

def update_kid_stars(stars_to_add):
    data = load_db()
    kid = data.setdefault('users', {}).setdefault('kid_profile', {'name': 'Bảo Nam', 'total_stars': 0})
    kid['total_stars'] += stars_to_add
    save_db(data)
    return kid['total_stars']

def deduct_kid_stars(stars_to_deduct):
    data = load_db()
    kid = data.setdefault('users', {}).setdefault('kid_profile', {'name': 'Bảo Nam', 'total_stars': 0})
    if kid['total_stars'] >= stars_to_deduct:
        kid['total_stars'] -= stars_to_deduct
        save_db(data)
        return True, kid['total_stars']
    return False, kid['total_stars']

def get_tasks():
    data = load_db()
    return data.get('tasks', {})

def add_pending_approval(task_id):
    data = load_db()
    pending = data.setdefault('pending_approvals', {})
    log_id = f"log_{int(datetime.now().timestamp())}"
    pending[log_id] = {
        'task_id': task_id,
        'timestamp': datetime.now().isoformat(),
        'status': 'pending'
    }
    save_db(data)

def mark_task_completed(task_id):
    """Đánh dấu nhiệm vụ đã hoàn thành hôm nay"""
    data = load_db()
    completions = data.setdefault('task_completions', {})
    today = datetime.now().strftime('%Y-%m-%d')
    today_completions = completions.setdefault(today, [])
    if task_id not in today_completions:
        today_completions.append(task_id)
    save_db(data)

def is_task_completed_today(task_id):
    """Kiểm tra nhiệm vụ đã hoàn thành hôm nay chưa"""
    data = load_db()
    completions = data.get('task_completions', {})
    today = datetime.now().strftime('%Y-%m-%d')
    return task_id in completions.get(today, [])

def is_task_pending_approval(task_id):
    """Kiểm tra nhiệm vụ đang chờ duyệt"""
    data = load_db()
    pending = data.get('pending_approvals', {})
    for log_id, log_data in pending.items():
        if log_data.get('task_id') == task_id and log_data.get('status') == 'pending':
            return True
    return False

def get_pending_approvals():
    data = load_db()
    return data.get('pending_approvals', {})

def approve_task(log_id, task_id, stars_reward):
    data = load_db()
    # Remove from pending
    if 'pending_approvals' in data and log_id in data['pending_approvals']:
        del data['pending_approvals'][log_id]
    
    # Add stars
    kid = data.setdefault('users', {}).setdefault('kid_profile', {'name': 'Bảo Nam', 'total_stars': 0})
    kid['total_stars'] += stars_reward
    
    # Mark task as completed today
    completions = data.setdefault('task_completions', {})
    today = datetime.now().strftime('%Y-%m-%d')
    today_completions = completions.setdefault(today, [])
    if task_id not in today_completions:
        today_completions.append(task_id)
    
    save_db(data)

def reject_task(log_id):
    data = load_db()
    if 'pending_approvals' in data and log_id in data['pending_approvals']:
        del data['pending_approvals'][log_id]
        save_db(data)

def get_rewards_pool():
    data = load_db()
    return data.get('rewards_pool', {})

def get_system_config():
    data = load_db()
    return data.get('system_config', {})

def update_system_config(key, value):
    data = load_db()
    config = data.setdefault('system_config', {})
    config[key] = value
    save_db(data)

def update_kid_name(new_name):
    data = load_db()
    kid = data.setdefault('users', {}).setdefault('kid_profile', {'name': 'Bảo Nam', 'total_stars': 0})
    kid['name'] = new_name
    save_db(data)

def save_task(task_id, title, icon, stars_reward, requires_approval, is_daily=False):
    data = load_db()
    tasks = data.setdefault('tasks', {})
    if not task_id:
        task_id = f"task_{int(datetime.now().timestamp())}"
    tasks[task_id] = {
        "title": title,
        "icon": icon,
        "stars_reward": stars_reward,
        "requires_approval": requires_approval,
        "is_daily": is_daily
    }
    save_db(data)

def delete_task(task_id):
    data = load_db()
    if 'tasks' in data and task_id in data['tasks']:
        del data['tasks'][task_id]
        save_db(data)

def save_reward(reward_id, name, probability, icon_url):
    data = load_db()
    rewards = data.setdefault('rewards_pool', {})
    if not reward_id:
        reward_id = f"reward_{int(datetime.now().timestamp())}"
    rewards[reward_id] = {
        "name": name,
        "probability": probability,
        "icon_url": icon_url
    }
    save_db(data)

def delete_reward(reward_id):
    data = load_db()
    if 'rewards_pool' in data and reward_id in data['rewards_pool']:
        del data['rewards_pool'][reward_id]
        save_db(data)

# ========== WEEKLY SCHEDULE ==========
DAYS_OF_WEEK = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
DAYS_VI = {
    'monday': 'Thứ Hai', 'tuesday': 'Thứ Ba', 'wednesday': 'Thứ Tư',
    'thursday': 'Thứ Năm', 'friday': 'Thứ Sáu', 'saturday': 'Thứ Bảy',
    'sunday': 'Chủ Nhật'
}

def get_weekly_schedule():
    data = load_db()
    return data.get('weekly_schedule', {})

def save_weekly_schedule(schedule):
    data = load_db()
    data['weekly_schedule'] = schedule
    save_db(data)

def get_today_day_key():
    """Trả về key ngày hôm nay: monday, tuesday..."""
    return datetime.now().strftime('%A').lower()

def get_tasks_for_today():
    """Lấy danh sách nhiệm vụ được gán cho ngày hôm nay theo lịch tuần và các nhiệm vụ hàng ngày"""
    schedule = get_weekly_schedule()
    today_key = get_today_day_key()
    task_ids = schedule.get(today_key, [])
    
    all_tasks = get_tasks()
    
    # Kết hợp các task có trong lịch tuần HOẶC được đánh dấu is_daily
    scheduled_tasks = {}
    for tid, tdata in all_tasks.items():
        if tid in task_ids or tdata.get('is_daily', False):
            scheduled_tasks[tid] = tdata
            
    # Nếu lịch tuần hoàn toàn trống (chưa setup bất kỳ ngày nào) và không có task daily nào
    if not schedule and not any(t.get('is_daily') for t in all_tasks.values()):
        return all_tasks
        
    return scheduled_tasks

def get_tasks_for_day(day_key):
    """Lấy danh sách nhiệm vụ cho 1 ngày cụ thể (bao gồm cả daily tasks)"""
    schedule = get_weekly_schedule()
    task_ids = schedule.get(day_key, [])
    all_tasks = get_tasks()
    
    return {tid: tdata for tid, tdata in all_tasks.items() if tid in task_ids or tdata.get('is_daily', False)}

# ========== REPORTS ==========
def get_completions_for_date(date_str):
    """Lấy danh sách task_id đã hoàn thành trong 1 ngày"""
    data = load_db()
    return data.get('task_completions', {}).get(date_str, [])

def get_weekly_report(start_date):
    """
    Lấy báo cáo hoạt động 7 ngày bắt đầu từ start_date (datetime.date).
    Trả về dict: {date_str: {completed: [...], scheduled: [...], rate: float}}
    """
    from datetime import timedelta
    all_tasks = get_tasks()
    schedule = get_weekly_schedule()
    report = {}
    
    for i in range(7):
        day = start_date + timedelta(days=i)
        date_str = day.strftime('%Y-%m-%d')
        day_key = day.strftime('%A').lower()
        
        scheduled_ids = schedule.get(day_key, [])
        # Lọc những task hợp lệ và tự động cộng thêm các task daily
        valid_scheduled_ids = []
        for tid, tdata in all_tasks.items():
            if tid in scheduled_ids or tdata.get('is_daily', False):
                valid_scheduled_ids.append(tid)
        
        scheduled_ids = valid_scheduled_ids
        completed_ids = get_completions_for_date(date_str)
        
        total = len(scheduled_ids) if scheduled_ids else 0
        done = len([c for c in completed_ids if c in scheduled_ids]) if scheduled_ids else len(completed_ids)
        rate = (done / total * 100) if total > 0 else 0
        
        report[date_str] = {
            'day_vi': DAYS_VI.get(day_key, day_key),
            'day_key': day_key,
            'scheduled': scheduled_ids,
            'completed': completed_ids,
            'done_count': done,
            'total_count': total,
            'rate': round(rate, 1)
        }
    
    return report
