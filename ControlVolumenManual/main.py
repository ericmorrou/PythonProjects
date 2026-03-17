import cv2
import time
import numpy as np
from datetime import datetime
from HandTrackingModule import HandDetector
from VolumeHandControl import VolumeController
from dao.mongodb_dao import MongoDBDAO
from models.session import Session
from models.volume_event import VolumeEvent
from config.settings import load_config

def main():
    # Load config and initialize DAO
    config = load_config()
    dao = MongoDBDAO()
    
    # Session tracking
    start_time = datetime.now()
    session = Session(start_time=start_time)
    
    # Camera and modules
    w_cam, h_cam = 640, 480
    cap = cv2.VideoCapture(0)
    cap.set(3, w_cam)
    cap.set(4, h_cam)
    
    detector = HandDetector(detection_con=0.7)
    vol_control = VolumeController()
    
    p_time = 0
    vol_per = 0
    vol_bar = 400
    
    current_vol = vol_control.get_current_volume()

    print("Main loop started. Press 'q' to quit.")

    try:
        while True:
            success, img = cap.read()
            if not success:
                break

            # 1. Find Hand
            img = detector.find_hands(img)
            lm_list, bbox = detector.find_position(img, draw=True)

            if len(lm_list) != 0:
                # 2. Check if little finger is down (gesture intention)
                fingers = detector.fingers_up()
                # fingers list: [thumb, index, middle, ring, pinky]
                # Pinky index is 4
                if fingers[4] == 0:
                    # 3. Find distance between index (8) and thumb (4)
                    length, img, line_info = detector.find_distance(4, 8, img)
                    
                    # 4. Map distance to volume
                    prev_vol = current_vol
                    vol_per, vol_bar = vol_control.set_volume(length)
                    current_vol = vol_control.get_current_volume()
                    
                    # 5. Save event if volume changed significantly
                    if abs(current_vol - prev_vol) > 0.1:
                        event = VolumeEvent(
                            prev_volume=float(prev_vol),
                            new_volume=float(current_vol),
                            distance=float(length)
                        )
                        dao.insert_volume_event(event)

            # Draw volume bar
            cv2.rectangle(img, (50, 150), (85, 400), (255, 0, 0), 3)
            cv2.rectangle(img, (50, int(vol_bar)), (85, 400), (255, 0, 0), cv2.FILLED)
            cv2.putText(img, f'{int(vol_per)} %', (40, 450), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 3)
            
            # FPS
            c_time = time.time()
            fps = 1 / (c_time - p_time)
            p_time = c_time
            cv2.putText(img, f'FPS: {int(fps)}', (40, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 3)
            
            # DB Status indicator
            status_color = (0, 255, 0) if dao.is_connected() else (0, 0, 255)
            status_text = "DB: OK" if dao.is_connected() else "DB: --"
            cv2.putText(img, status_text, (40, 90), cv2.FONT_HERSHEY_COMPLEX, 0.7, status_color, 2)

            cv2.imshow("Hand Volume Control", img)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    finally:
        # Finalize session
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        session.end_time = end_time
        session.duration = duration
        dao.insert_session(session)
        
        cap.release()
        cv2.destroyAllWindows()
        print("Application closed.")

if __name__ == "__main__":
    main()
