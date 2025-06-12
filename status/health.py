import time
from .constants import HEALTH_CHECK_INTERVAL

def update_health(status):
    now = time.time()

    # 각 상태별 체크 및 페널티 관리
    for key in ["mood", "fatigue", "hunger"]:
        fault_key = f"{key}_fault_time"

        # 상태가 0이 되었을 때
        if status[key] <= 0:
            # 처음 0이 된 경우 → 즉시 -10
            if fault_key not in status or status[fault_key] is None:
                status["health"] = max(0, status["health"] - 10)
                status[fault_key] = now
            # 이미 fault_time이 있고, 5분 지났으면 → 추가로 -5
            elif now - status[fault_key] >= HEALTH_CHECK_INTERVAL:
                status["health"] = max(0, status["health"] - 5)
                status[fault_key] = now  # 다음 주기를 위해 갱신

        else:
            # 0이 아닌 상태로 회복되면 타이머 초기화
            status[fault_key] = None
