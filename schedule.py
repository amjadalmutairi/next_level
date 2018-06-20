from app import generate_pdf
from apscheduler.schedulers.background import BackgroundScheduler
import db
import datetime
import calendar
import os
import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import sys

scheduler = BackgroundScheduler()
COMMASPACE = ', '
def scheduler_job():
    user = db.get_user_info()
    year = datetime.datetime.now().year
    month = datetime.datetime.now().month
    date = "%d-%02d" % (year, month)
    days = db.get_month_days(month,year)
    path = os.path.join(os.path.expanduser("~"), "Desktop/", date + ".pdf")
    title = "%s - %d Performance Report for %s" % (calendar.month_abbr[month],year,user.name)
    generate_pdf(path,title,days)
    hasSent = send_email(path,date,user)
    db.insert_report(user,year,month,hasSent)
    os.remove(path)

def send_email(path,date,user):
    sender = user.email
    gmail_password = user.password.decode('utf-8')
    recipients = [user.email]

    # Create the enclosing (outer) message
    outer = MIMEMultipart()
    outer['Subject'] = '%s Performance Report' % date
    outer['To'] = COMMASPACE.join(recipients)
    outer['From'] = sender
    outer.preamble = 'You will not see this in a MIME-aware mail reader.\n'

    # List of attachments
    attachments = [path]
     # Add the attachments to the message
    for file in attachments:
        try:
            with open(file, 'rb') as fp:
                msg = MIMEBase('application', "octet-stream")
                msg.set_payload(fp.read())

            encoders.encode_base64(msg)
            msg.add_header('Content-Disposition', 'attachment', filename=os.path.basename(file))
            outer.attach(msg)
            outer.attach(MIMEText("Hi %s, \nPlease find attached your monthly report!\nHave a nice day <3." %user.name, 'plain'))
        except:
            return False
        composed = outer.as_string()

    # Send the email
    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as s:
            s.ehlo()
            s.starttls()
            s.ehlo()
            s.login(sender, gmail_password)
            s.sendmail(sender, recipients, composed)
            s.close()
        return True
    except:
        return False

scheduler.add_job(scheduler_job,'cron', day='last', hour='9')

#Un-comment the following line to Test the scheduler
# scheduler.add_job(scheduler_job,'cron', next_run_time=datetime.datetime.now())

scheduler.start()
print(scheduler.running) #Should prints true

# Un-comment this to stop the scheduler
# scheduler.shutdown()
# print(scheduler.running)
