
ffmpeg -video_size 1300x700 -framerate 30 -f x11grab -i :0.0+0,0 -codec:v libx264 -preset ultrafast record.mp4

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

raw_str = pygame.image.tostring(screen, 'RGB')
frame = np.frombuffer(raw_str, dtype=np.uint8).reshape((HEIGHT, WIDTH, 3))
frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
video_writer.write(frame)
