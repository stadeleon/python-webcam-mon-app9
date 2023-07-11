import glob
import os
import time
import cv2
from mailer import send_email
import asyncio
from threading import Thread

stop_event = asyncio.Event()


def clean_images_folder(img_folder_path='images/'):
    images = glob.glob(f"{img_folder_path}*.png")
    for image in images:
        os.remove(image)


async def main():
    loop = asyncio.get_running_loop()

    def email_and_clean(image_path, count_queue):
        success, error = send_email(image_path)
        if success:
            print("Email sent successfully.")
            clean_images_folder()
            loop.call_soon_threadsafe(count_queue.put_nowait, 1)
        else:
            print("Error sending email:", error)

    video = cv2.VideoCapture(0)
    time.sleep(1)

    base_frame = None
    status_list = []
    count = 1
    count_queue = asyncio.Queue()

    try:
        while not stop_event.is_set():
            status = 0
            check, frame = video.read()

            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray_frame_gau = cv2.GaussianBlur(gray_frame, (21, 21), 0)

            if base_frame is None:
                base_frame = gray_frame_gau

            delta_frame = cv2.absdiff(base_frame, gray_frame_gau)
            threshold_frame = cv2.threshold(delta_frame, 90, 255, cv2.THRESH_BINARY)[1]
            dilated_frame = cv2.dilate(threshold_frame, None, iterations=2)
            cv2.imshow("My video", dilated_frame)

            contours, check = cv2.findContours(dilated_frame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            for contour in contours:
                if cv2.contourArea(contour) < 5000:
                    continue
                x, y, w, h, = cv2.boundingRect(contour)
                rectangle = cv2.rectangle(frame, (x, y,), (x+w, y+h), (0, 255, 0), 3)

                if rectangle.any():
                    status = 1
                    cv2.imwrite(f"images/{count}.png", frame)
                    count += 1
                    all_images = glob.glob("images/*.png")
                    index = int(len(all_images) / 2)
                    image_with_object = all_images[index]

            status_list.append(status)
            status_list = status_list[-2:]

            if status_list[0] == 1 and status_list[1] == 0:
                email_thread = Thread(target=email_and_clean, args=(image_with_object, count_queue))
                email_thread.daemon = True
                email_thread.start()

            if not count_queue.empty():
                count = await count_queue.get()

            cv2.imshow("Video", frame)

            key = cv2.waitKey(1)

            if key == ord('q'):
                stop_event.set()
                break

            if key == ord('p'):
                cv2.imwrite('my_framed_image.png', delta_frame)

    finally:
        video.release()
        clean_images_folder()

asyncio.run(main())
