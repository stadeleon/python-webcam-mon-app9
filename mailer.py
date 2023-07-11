import os
import smtplib
import imghdr
from dotenv import load_dotenv
from email.message import EmailMessage

load_dotenv()

mailer_host = os.getenv('EMAIL_HOST')
mailer_port = int(os.getenv('EMAIL_PORT'))
username = os.getenv('USERNAME')
password = os.getenv('PASSWORD')
recipient = os.getenv('RECIPIENT')


def send_email(image_path):
    email_message = EmailMessage()
    email_message["Subject"] = "Motion Detection"
    email_message["From"] = f"Motion Detector <{recipient}>"
    email_message["To"] = f"Leonid Derevianko <{recipient}>"

    with open(image_path, "rb") as file:
        content = file.read()
        img_type = imghdr.what(None, content)

    email_message.add_alternative(f"""\
<html>
<div>
    <h1>Hey!</h1>
    <p>It's Something happening there!</p>
</body>
</html>
""", subtype='html')

    email_message.add_attachment(
        content,
        maintype="image",
        subtype=img_type,
        filename=f'intruder.{img_type}'
    )
    try:
        with smtplib.SMTP(host=mailer_host, port=mailer_port) as srv:
            srv.starttls()
            srv.login(username, password)
            srv.sendmail(recipient, recipient, email_message.as_string())

        return True, None
    except smtplib.SMTPException as e:
        return False, str(e)


if __name__ == '__main__':
    success, error = send_email('images/12.png')
    if success:
        print("Email sent successfully.")
    else:
        print("Error sending email:", error)