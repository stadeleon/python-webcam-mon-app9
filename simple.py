import streamlit as st
import cv2
import calendar
from datetime import datetime

st.title("Motion Detector Web-app")
start = st.button('Start Camera')

if start:
    streamlit_image = st.image([])
    camera = cv2.VideoCapture(0)

    while True:
        check, frame = camera.read()
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        current_day = datetime.now()
        text_time = current_day.strftime("%H:%M:%S")
        weekday = current_day.weekday()

        cv2.putText(img=frame, text=calendar.day_name[weekday], org=(50, 50),
                    fontFace=cv2.FONT_HERSHEY_PLAIN, fontScale=2, color=(255, 255, 255),
                    thickness=2, lineType=cv2.LINE_AA
                    )

        cv2.putText(img=frame, text=text_time, org=(50, 100),
                    fontFace=cv2.FONT_HERSHEY_PLAIN, fontScale=2, color=(250, 0, 50),
                    thickness=2, lineType=cv2.LINE_AA
                    )
        streamlit_image.image(frame)