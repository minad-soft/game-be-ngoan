# 🚀 Antigravity Project Blueprint: Space Rewards 

**Ngày khởi tạo:** 2026-05-08
**Trạng thái:** 🟢 Ready for Execution / Sẵn sàng triển khai
**Mô tả ngắn gọn:** Hệ thống Game tương tác (phát triển trên Streamlit + Firebase) giúp bé hoàn thành nhiệm vụ để tích lũy "Sao", mở khóa túi mù "Phi thuyền con thoi" và đổi quà. Tích hợp phân quyền Phụ huynh - Trẻ em an toàn với mã PIN và phép toán.

---

## 🎯 1. Mục tiêu dự án (Objectives)
* **Trải nghiệm Game hóa (Gamification):** UI/UX không mang cảm giác "ứng dụng văn phòng". Sử dụng Lottie animations, hiệu ứng hạt (balloons/snow) và CSS tùy chỉnh để tạo không gian vũ trụ sinh động.
* **Bảo mật 2 Lớp (Parent Mode):** Bảo vệ khu vực quản lý bằng mã PIN tĩnh 4 số kết hợp với một phép toán ngẫu nhiên (trình độ lớp 3-4).
* **Quản lý Dòng điểm:** Hệ thống phân loại nhiệm vụ (Tự động cộng sao vs. Chờ ba mẹ duyệt) để chống spam click.
* **Lưu trữ Real-time:** Sử dụng Firebase Realtime Database để đồng bộ tức thời giữa thao tác duyệt của ba mẹ và màn hình hiển thị của bé.

## 🤖 2. Hệ sinh thái AI Agents (Agent Roster)

| Tên Agent | Vai trò (Role) | Nhiệm vụ chính (Tasks) | Công cụ cấp phép (Tools) |
| :--- | :--- | :--- | :--- |
| **Visual_Designer** | Giám đốc Nghệ thuật | Xây dựng hàm render UI/UX trên Streamlit. Ghi đè CSS gốc để tạo nút bấm lớn, bo tròn, tích hợp emoji và Lottie animations. | `streamlit`, `streamlit-lottie`, `Custom CSS` |
| **Data_Manager** | Kỹ sư Dữ liệu | Xử lý các tác vụ CRUD (Create, Read, Update, Delete) với Firebase. Đảm bảo cấu trúc JSON gọn nhẹ và truy xuất nhanh. | `firebase-admin`, `json_parser` |
| **Gamification_Engine**| Kỹ sư Game Logic | Quản lý logic tính toán: Cộng/trừ sao, check điều kiện mở Phi thuyền, và thuật toán quay thưởng ngẫu nhiên (gacha) dựa trên tỷ lệ phần trăm. | `python_executor`, `random` |
| **Parent_Gatekeeper** | Người gác cổng | Sinh ra bài toán ngẫu nhiên (nhân/chia 2 chữ số), kiểm tra mã PIN và quản lý trạng thái phiên làm việc (Session State) để cấp quyền vào Dashboard quản lý. | `math_generator`, `Session_State` |

## 🗄️ 3. Cấu trúc Database Đề xuất (Firebase JSON)
```json
{
  "system_config": {
    "parent_pin": "1234",
    "stars_required_for_blindbag": 50
  },
  "users": {
    "kid_profile": {
      "name": "Bảo Nam",
      "total_stars": 120
    }
  },
  "tasks": {
    "task_1": {
      "title": "Sắp xếp bàn học",
      "icon": "🧹",
      "stars_reward": 5,
      "requires_approval": false,
      "cooldown_hours": 12
    },
    "task_2": {
      "title": "Đọc 1 chương sách",
      "icon": "📚",
      "stars_reward": 15,
      "requires_approval": true 
    }
  },
  "rewards_pool": {
    "reward_1": {
      "name": "Đi ăn kem",
      "probability": 60,
      "icon_url": "link_to_image"
    },
    "reward_2": {
      "name": "Mua bộ Lego nhỏ",
      "probability": 10,
      "icon_url": "link_to_image"
    }
  },
  "pending_approvals": {
    "log_1": {
      "task_id": "task_2",
      "timestamp": "2026-05-08T14:30:00",
      "status": "pending"
    }
  }
}