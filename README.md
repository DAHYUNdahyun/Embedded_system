메인 화면
- 글꼴 설정
- 음식 생성 범위 조정 및 캐릭터 변화
- 휴식 모드 : 3개 중 제일 오른쪽 버튼 클릭, 화면 어두워짐, 상태바 제외 모든 행동 중지, 캐릭터 변화
- 진화 모드 : 전체 100에서 25 단위로 진화, 캐릭터 변화까지 확인

+) 개선
- 음식 사진 만들어서 랜덤으로 생성
- 캐릭터 사진 추가
- 게임 연결 필요
- 센서 연결

상태바
- 센서 없이 시간 흐르면 변화하는 요소 확인 완료
(기분 나쁠 때 이미지 변화, 밥 먹을 때 배고픔 상승, 요건 달성시 진화 게이지 참)

+) 개선
- 상태바 배경 디자인

게임 선택 창
- 각 게임 누르면 그 게임 창으로 이동

게임
- 생명 3개 (하트, 빈 하트 이미지) - 0개가 되면 R 버튼을 눌러 재시작
- 슈팅 게임
  - 적과 충돌하거나 적이 바닥까지 닿으면(못 죽이면) 생명 1 감소, 죽이면 score 1 증가
- 러닝 게임
  - 허들에 충돌하면 생명 1 감소, 포인트를 먹으면 score 1 증가
- 피하기 게임
  - 적과 충돌하면 생명 1 감소, 적을 피하면 score 1 증가
 
+) 개선 -완료
- 각 게임에서 나가서 게임 선택 창에서 다시 게임 선택하는 나가기 버튼 추가
- 게임 디자인 개선

# 설명서 텍스트 전체
instruction_pages = [
    [
        "📘 소개",
        "이 다마고치는 단순한 가상 펫이 아닙니다.",
        "라즈베리파이와 다양한 센서를 활용한",
        "인터랙티브 스마트 반려 생명체입니다.",
        "환경을 감지하고, 사용자와 소통하며,",
        "진화하고, 게임도 함께 즐깁니다!",
    ],
    [
        "📦 주요 기능",
        "🧠 AI 감정 시스템",
        "온도/습도에 따라 기분이 변하고,",
        "음식, 피로, 게임 활동 등으로 상태가 반영됩니다.",
        "🌡️ DHT11 센서로 온습도 감지",
        "쾌적한 환경이면 기분이 좋아지고,",
        "덥거나 습하면 슬퍼져요!"
    ],
    [
        "🔦 조도 센서 (빛 감지)",
        "어두운 환경에서는 잠에 빠지고,",
        "밝아지면 자동으로 깨어납니다.",
        "🎮 세 가지 미니게임 내장",
        "슈팅 게임 / 러닝 게임 / 회피 게임",
        "게임으로 피로도를 회복할 수 있어요!"
    ],
    [
        "🍖 먹이주기 기능",
        "직접 먹이를 소환해서 배불리 먹이세요!",
        "😵 기울임 반응 (Tilt 센서)",
        "다마고치를 심하게 흔들면 어지러워해요...",
        "🔊 부저 멜로디",
        "모든 상태가 만족스러우면",
        "기분 좋은 소리를 들려줘요!"
    ],
    [
        "💡 사용 방법",
        "전원을 켜면 시작 화면이 나타납니다.",
        "닉네임을 설정하면 부화해요.",
        "UI 버튼과 터치센서로 상호작용할 수 있어요.",
        "왼쪽 버튼: 메인 화면",
        "가운데 버튼: 게임 선택",
        "오른쪽 버튼: 휴식 모드 전환",
        "다양한 자극에 반응하는 다마고치를 관찰해보세요!"
    ]
]


def draw_instruction_screen(screen, font_obj, page=0):
    screen.fill(WHITE)
    title_font = pygame.font.SysFont("Arial", 36, bold=True)
    draw_text_center(screen, "Instruction Manual", 60, (0, 0, 0), title_font)

    if page < 0 or page >= len(instruction_pages):
        return

    for i, line in enumerate(instruction_pages[page]):
        draw_text_center(screen, line, 140 + i * 36, font_obj=font_obj)

    # 페이지 넘김 안내
    tip = f"← {page+1}/{len(instruction_pages)} →"
    draw_text_center(screen, tip, screen.get_height() - 60, (100, 100, 100), font_obj)


elif state == "instruction":
    draw_instruction_screen(screen, font_start, instruction_page)

    if keys:
        if "LEFT" in nk:
            instruction_page = max(0, instruction_page - 1)
        elif "RIGHT" in nk:
            instruction_page = min(len(instruction_pages) - 1, instruction_page + 1)
        elif "D" in nk or "C" in nk or "ENTER" in nk:
            state = "nickname"
            nickname = ""
            vk_row, vk_col = 0, 0


instruction_page = 0
