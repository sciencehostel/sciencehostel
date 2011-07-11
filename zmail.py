import os
import sys
import smtplib
import urllib
# For guessing MIME type based on file name extension
import mimetypes
from email import encoders
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from BeautifulSoup import BeautifulSoup
import pickle
import logging

COMMASPACE = ', '

def Send(sender, receiver, msg):
    server = smtplib.SMTP('smtp.gmail.com',587)
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login('dont-reply@sciencehostel.org','e8physics')
    server.sendmail(sender, receiver, msg)
    server.close()

def SendTo(receiver, subject, content):
    outer = MIMEMultipart()
    outer['Subject'] = subject
    outer['To'] = COMMASPACE.join(receiver)
    outer['From'] = 'Science Hostel<dont-reply@sciencehostel.org>'

    txt = MIMEText(content, 'html')
    outer.attach(txt)
    for recv in receiver:
        logging.info('sending to %s' % recv)
        Send('dont-reply@sciencehostel.org', recv, outer.as_string())


