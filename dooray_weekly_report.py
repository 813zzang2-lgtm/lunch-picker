"""
두레이 주간보고 Task 자동 생성 스크립트
- 매주 수요일 14시에 자동 실행
- 포인트-주간보고 프로젝트에 task 생성
- 프로젝트 멤버 8명 자동 담당자 등록
- 생성 후 나에게 보내기 채널로 알림 전송
"""

import requests
import datetime

# =============================================
# ✏️ 여기만 수정하세요
DOORAY_API_TOKEN = "ajjt1imxmtj4:yEYzwAK_R9iid80SeSoJyw"
PROJECT_ID = "3880705043841564116"  # 포인트-주간보고
NOTIFY_WEBHOOK_URL = "https://nhnent.dooray.com/services/1916324552942047592/4307376659886325981/0rigD1_xS8OrqEyuaM2G8A"

# 프로젝트 멤버 전체 (담당자로 등록)
MEMBER_IDS = [
    "2183490686534482112",
    "3152528377927654344",
    "2178414738795888452",
    "4223068200695389635",
    "3381561264923168632",
    "3431565838396031252",
    "3619280140656492484",
    "1651817638313208845",
]
# =============================================

DOORAY_API_URL = "https://api.dooray.com"


def get_next_thursday() -> datetime.date:
    today = datetime.date.today()
    days_until_thursday = (3 - today.weekday()) % 7
    if days_until_thursday == 0:
        days_until_thursday = 7
    return today + datetime.timedelta(days=days_until_thursday)


def get_task_title() -> str:
    thursday = get_next_thursday()
    date_str = thursday.strftime("%y/%m/%d")
    return f"[{date_str}] 개인별 주간업무보고 - 목요일 오후 2시까지"


def get_task_body() -> str:
    return """## 📋 주간업무보고 템플릿

아래 표를 복사하여 본인 업무를 작성해주세요.

---

### 1. 이번 주 업무 현황

| 업무명 | 업무 구분 | 완료목표일 | 업무 현황<br>(이번주 진행한것 / 진행한 날짜) | 업무 현황<br>(다음주 진행할 것 / 요청 또는 보고할 날짜) | 의사결정 필요사항 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 업무 대구분 | 소구분 | 일자 | 이번주에 진행한 업무 현황 자세히<br>**업무 진행 두레이 링크**<br>*(해당 두레이 참조에 팀장님을 넣어주세요)* | 다음주 진행할 업무 현황 자세히 | 조직장(팀장/사업이사)<br>의사결정 필요 사항 기재 |

---
> ⚠️ 목요일 오후 2시까지 작성!
"""


def create_task():
    headers = {
        "Authorization": f"dooray-api {DOORAY_API_TOKEN}",
        "Content-Type": "application/json"
    }

    title = get_task_title()
    body = get_task_body()
    thursday = get_next_thursday()
    due_date = f"{thursday.strftime('%Y-%m-%d')}T14:00:00+09:00"

    users_to = [
        {"type": "member", "member": {"organizationMemberId": mid}}
        for mid in MEMBER_IDS
    ]

    payload = {
        "subject": title,
        "body": {
            "mimeType": "text/x-markdown",
            "content": body
        },
        "dueDate": due_date,
        "dueDateFlag": True,
        "users": {
            "to": users_to
        }
    }

    try:
        response = requests.post(
            f"{DOORAY_API_URL}/project/v1/projects/{PROJECT_ID}/posts",
            headers=headers,
            json=payload,
            timeout=10
        )
        data = response.json()

        if response.status_code in [200, 201] and data.get("header", {}).get("isSuccessful"):
            task_id = data.get("result", {}).get("id", "")
            task_url = f"https://nhnent.dooray.com/project/tasks/{task_id}"
            print(f"✅ Task 생성 완료!")
            print(f"   제목: {title}")
            print(f"   마감: {thursday.strftime('%Y-%m-%d')} 14:00")
            print(f"   담당자: {len(MEMBER_IDS)}명 등록")
            print(f"   링크: {task_url}")
            return title, task_url
        else:
            print(f"❌ Task 생성 실패: {data}")
            return None, None

    except Exception as e:
        print(f"❌ Task 생성 오류: {e}")
        return None, None


def send_notification(title: str, task_url: str):
    thursday = get_next_thursday()
    message = (
        f"📋 *주간보고 Task가 생성되었습니다!*\n\n"
        f"제목: {title}\n"
        f"마감: {thursday.strftime('%Y년 %m월 %d일')} 오후 2시\n"
        f"링크: {task_url}"
    )

    payload = {"text": message}
    try:
        response = requests.post(NOTIFY_WEBHOOK_URL, json=payload, timeout=10)
        if response.status_code == 200:
            print("✅ 채팅 알림 전송 완료!")
        else:
            print(f"❌ 알림 전송 실패: {response.status_code}")
    except Exception as e:
        print(f"❌ 알림 전송 오류: {e}")


def main():
    print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}] 주간보고 Task 생성 시작")
    title, task_url = create_task()
    if title and task_url:
        send_notification(title, task_url)
    else:
        print("❌ Task 생성 실패로 알림을 보내지 않습니다.")


if __name__ == "__main__":
    main()
