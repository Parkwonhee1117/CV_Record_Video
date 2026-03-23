import cv2 as cv
import datetime

cap = cv.VideoCapture("rtsp://210.99.70.120:1935/live/cctv001.stream")

# 비디오 설정을 위한 정보 가져오기
width = int(cap.get(cv.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv.CAP_PROP_FRAME_HEIGHT))
fps = cap.get(cv.CAP_PROP_FPS)
if fps == 0 or fps > 60: fps = 20.0 # 주소에 따라 FPS를 못 가져올 경우 대비

# 코덱 설정 (FourCC)
fourcc = cv.VideoWriter_fourcc(*'XVID')
out = None

# 상태 변수들
is_recording = False
is_paused = False

print("연결 시도 중... (RTSP 주소가 유효해야 합니다)")
print("Space: 녹화 시작/중지 | S: 일시정지 | ESC: 종료")

while True:
    # 일시정지 상태가 아닐 때만 새로운 프레임을 읽음
    if not is_paused:
        ret, frame = cap.read()
        if not ret:
            print("영상을 읽을 수 없습니다.")
            break
        
        display_frame = frame.copy()
        
        # 현재 시간 표시
        now = datetime.datetime.now().strftime("%Y-%m-d %H:%M:%S")
        cv.putText(display_frame, now, (10, height - 20), 
                   cv.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

    # 일시정지 상태일 때 화면 표시
    else:
        # 화면 중앙에 PAUSED 문구 표시
        cv.putText(display_frame, "PAUSED", (width//2 - 100, height//2), 
                   cv.FONT_HERSHEY_SIMPLEX, 1.5, (255, 0, 0), 3)

    # 녹화 중일 때 (일시정지 중에는 녹화도 잠시 멈춤)
    if is_recording and not is_paused:
        # 화면 왼쪽 상단에 빨간색 녹화 표시
        cv.circle(display_frame, (30, 30), 10, (0, 0, 255), -1)
        cv.putText(display_frame, "REC", (50, 40), cv.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        if out is not None:
            out.write(frame)

    # 최종 결과 화면 출력
    cv.imshow('Smart Video Recorder', display_frame)

    key = cv.waitKey(1) & 0xFF

    # 1. Space 키: 녹화 시작/중지
    if key == ord(' '):
        is_recording = not is_recording
        if is_recording:
            # 파일명을 현재 시간으로 설정
            filename = datetime.datetime.now().strftime("%Y%m%d_%H%M%S.avi")
            out = cv.VideoWriter(filename, fourcc, fps, (width, height))
            print(f"녹화 시작: {filename}")
        else:
            if out is not None:
                out.release()
                out = None
            print("녹화 종료 및 저장 완료")

    # 2. 's' 또는 'S' 키: 일시정지
    elif key == ord('s') or key == ord('S'):
        is_paused = not is_paused
        state = "일시정지" if is_paused else "재개"
        print(f"영상 {state}")

    # 3. ESC 키: 프로그램 종료
    elif key == 27:
        break

# 메모리 해제
cap.release()
if out is not None:
    out.release()
cv.destroyAllWindows()