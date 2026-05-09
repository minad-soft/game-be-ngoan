import json
import os
from datetime import datetime

DB_FILE = 'database.json'

def load_db():
    if not os.path.exists(DB_FILE):
        return {}
    with open(DB_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_db(data):
    with open(DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

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

def save_task(task_id, title, icon, stars_reward, requires_approval):
    data = load_db()
    tasks = data.setdefault('tasks', {})
    if not task_id:
        task_id = f"task_{int(datetime.now().timestamp())}"
    tasks[task_id] = {
        "title": title,
        "icon": icon,
        "stars_reward": stars_reward,
        "requires_approval": requires_approval
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
    """Lấy danh sách nhiệm vụ được gán cho ngày hôm nay theo lịch tuần"""
    schedule = get_weekly_schedule()
    today_key = get_today_day_key()
    task_ids = schedule.get(today_key, [])
    
    all_tasks = get_tasks()
    if not task_ids:
        # Nếu chưa setup lịch tuần, trả về tất cả tasks
        return all_tasks
    
    return {tid: all_tasks[tid] for tid in task_ids if tid in all_tasks}

def get_tasks_for_day(day_key):
    """Lấy danh sách nhiệm vụ cho 1 ngày cụ thể"""
    schedule = get_weekly_schedule()
    task_ids = schedule.get(day_key, [])
    all_tasks = get_tasks()
    return {tid: all_tasks[tid] for tid in task_ids if tid in all_tasks}

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
        # Lọc chỉ giữ lại task_id hợp lệ (vẫn tồn tại)
        scheduled_ids = [tid for tid in scheduled_ids if tid in all_tasks]
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
