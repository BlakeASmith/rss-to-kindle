from pathlib import Path
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.header import Header


def send_mail(
    from_address: str,
    password: str,
    to_address: str,
    subject: str,
    body: str,
    html_attach: Path,
):
    # create message object
    message = MIMEMultipart()
 
    # add in header
    message['From'] = Header(from_address)
    message['To'] = Header(to_address)
    message['Subject'] = Header(subject)
 
    # attach message body as MIMEText
    message.attach(MIMEText(body, 'plain', 'utf-8'))

    # locate and attach desired attachments
    att_name = html_attach.name
    _f = open(html_attach, 'rb')
    att = MIMEApplication(_f.read(), _subtype="txt")
    _f.close()
    att.add_header('Content-Disposition', 'attachment', filename=att_name)
    message.attach(att)
 
    # setup email server
    server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
    server.login(from_address, password)
 
    # send email and quit server
    server.sendmail(from_address, to_address, message.as_string())
    server.quit()

