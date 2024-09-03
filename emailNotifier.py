from email.mime.text import MIMEText
import smtplib

def send_email(email, msg):
    from_email = "grasssticksupdater@gmail.com"
    from_password ="ziid hmjz suci yfqr"
    to_email = email

    subject = msg
    message = msg

    msg = MIMEText(message, 'html')
    msg['Subject'] = subject
    msg['To'] = to_email
    msg['From'] = from_email

    gmail = smtplib.SMTP('smtp.gmail.com', 587)
    gmail.ehlo()
    gmail.starttls()
    gmail.login(from_email, from_password)
    gmail.send_message(msg)

if __name__ == '__main__':
    send_email("cabotmctavish2@gmail.com")
