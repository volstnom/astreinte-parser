# coding: utf-8

import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText

msg = MIMEMultipart()
msg['From'] = 'pyactemium@gmail.com'
msg['To'] = 'pierre-yves.lecoquil@actemium.com'
msg['Subject'] = 'Le sujet de mon mail' 
message = 'Bonjour !'
msg.attach(MIMEText(message))
mailserver = smtplib.SMTP('smtp.gmail.com', 587)
mailserver.ehlo()
mailserver.starttls()
mailserver.ehlo()
mailserver.login('pyactemium@gmail.com', 'fzdyzhnktadchaop')
mailserver.sendmail('pyactemium@gmail.com', 'pierre-yves.lecoquil@actemium.com', msg.as_string())
mailserver.quit()