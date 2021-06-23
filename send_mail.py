#!/bin/python3
import smtplib
from email.message import EmailMessage

global SENDER, SMTP_HOST, SMTP_PORT
SENDER='abc@123.com'
SMTP_HOST = 'localhost'
SMTP_PORT = 25

def sendMail(sender=SENDER,receivers=[],subject=None,message=None):
  msg = EmailMessage()
  msg.set_content(message)
  msg['Subject'] = subject
  msg['From'] = sender
  msg['To'] = receivers
  with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as s:
    s.send_message(msg)
