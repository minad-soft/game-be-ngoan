import random
import db_helper

def spin_gacha():
    """
    Quay thưởng ngẫu nhiên dựa trên xác suất cấu hình trong cơ sở dữ liệu.
    """
    rewards_pool = db_helper.get_rewards_pool()
    if not rewards_pool:
        return None
    
    # Chuẩn bị danh sách phần thưởng và trọng số (xác suất)
    rewards = []
    weights = []
    
    for reward_id, data in rewards_pool.items():
        rewards.append(data)
        weights.append(data.get('probability', 0))
    
    # Tính tổng xác suất
    total_weight = sum(weights)
    if total_weight <= 0:
        return None
        
    # Quay thưởng (dùng random.choices)
    chosen_reward = random.choices(rewards, weights=weights, k=1)[0]
    return chosen_reward
