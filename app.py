
from colorama import Fore, Back, Style
from validate_email import validate_email
from user import User
import db
from day import Day, rating_scale
import datetime
import sys
import calendar
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle,Paragraph,Spacer
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.pagesizes import letter, inch
import os

def read_positive_number(msg,less_than=sys.maxsize):
	value = input(Fore.BLUE + msg + Style.RESET_ALL)
	while ((not value.isdigit()) or int(value) < 0 or int(value) > less_than) :
		print(Fore.RED + "\n>> WRONG INPUT . ." + Style.RESET_ALL)
		value = input(Fore.BLUE + msg + Style.RESET_ALL)
	return int(value)

def read_rating_value(msg):
	rating_str = '''%d : %s\n%d : %s\n%d : %s\n%d : %s\n%d : %s\n''' %(rating_scale.EXCELLENT.value, rating_scale.EXCELLENT.name,
	rating_scale.VERY_GOOD.value, rating_scale.VERY_GOOD.name,
	rating_scale.GOOD.value, rating_scale.GOOD.name,
	rating_scale.FAIR.value, rating_scale.FAIR.name,
	rating_scale.POOR.value, rating_scale.POOR.name)

	value = input(Fore.BLUE + msg + Style.RESET_ALL + Fore.MAGENTA +  rating_str + Style.RESET_ALL )
	while ((not value.isdigit()) or int(value) < 0 or int(value) > 5 ) :
		print(Fore.RED + "\n>> WRONG INPUT . ." + Style.RESET_ALL)
		value = input(Fore.BLUE + msg + Style.RESET_ALL + Fore.MAGENTA +  rating_str + Style.RESET_ALL)
	return int(value)

def set_up():
	db.create_db()
	welcome_text = '''
(\__/)
(•ㅅ•)
/ 　 づ ♥
WELCOME INTO YOUR NEXT LEVEL!
-----------------------------'''
	print(Fore.BLUE  + Style.BRIGHT + welcome_text + Style.RESET_ALL)
	print(Fore.CYAN + Style.BRIGHT + str(datetime.date.today()) + ", " +
		calendar.day_name[datetime.datetime.today().weekday()] + Style.RESET_ALL)
	print(Fore.MAGENTA + Back.WHITE + Style.BRIGHT + "\n Oooh! It seems we got a new sweet user ♥‿♥ \n" + Style.RESET_ALL )
	user = read_configration()
	user.id = db.insert_new_user(user)
	return user

def read_configration():
	name = input( Fore.YELLOW + Style.BRIGHT + "* Your full name: " +  Style.RESET_ALL)
	email = input(Fore.YELLOW + Style.BRIGHT + "* Your email (Should be gmail): " +  Style.RESET_ALL)
	is_valid = validate_email(email.lower()) and "gmail.com" in email.lower()
	while((not is_valid) or ( "gmail.com" not in email.lower())):
		print(Fore.RED + "\n>> WRONG EMAIL ADDRESS . ." + Style.RESET_ALL)
		email = input(Fore.YELLOW + Style.BRIGHT + "* Your email (Should be gmail): " +  Style.RESET_ALL)
		is_valid = validate_email(email.lower()) and "gmail.com" in email.lower()
	password = input( Fore.YELLOW + Style.BRIGHT + "* Your email password: " +  Style.RESET_ALL)
	while password == "":
		print(Fore.RED + "\n>> PASSWORD CAN NOT BE EMPTY . ." + Style.RESET_ALL)
		password = input( Fore.YELLOW + Style.BRIGHT + "* Your email password: " +  Style.RESET_ALL)
	user = User(name,email.lower(),password)
	return user

def read_day_input(date):
	total = read_positive_number("Enter tasks total number of your todo list: ")
	completed = read_positive_number("Out of %d, how many did you complete? " % total , total)
	social = read_rating_value("How much do you rate your socila activity today?\n")
	health = read_rating_value("How much do you rate your health today?\n")
	overall = read_rating_value("Your overall rate for your day?\n")
	note = input(Fore.BLUE + "Any final note? (press enter directly if you have nothing) " + Style.RESET_ALL)
	day = Day(user.id,date,total,completed,social,health,overall,note)
	return day

def edit_day():
	print(Fore.MAGENTA + "\n======= Edit Day =======")
	d = read_positive_number("Enter the day: ",30)
	m = read_positive_number("Enter the month: ",12)
	y = read_positive_number("Enter the year: ",datetime.datetime.now().year)
	date = "%d-%02d-%02d"%(y,m,d)
	day = db.get_day(date)
	if day != None:
		print(day)
		id = day.id
		day = read_day_input(date)
		day.id = id
		db.update_day(day)
	else:
		print(Fore.WHITE + Back.RED + "\nThere is no stored data for the entered day " + date + "!" + Style.RESET_ALL + "\n" )

def edit_configration(user):
	print(Fore.MAGENTA + "\n======= Edit Configration =======")
	id = user.id
	user = read_configration()
	user.id = id
	db.update_user(user)
	return user

def generate_pdf(path,title_para,days):
	c = SimpleDocTemplate(path)
	table_data = [["Day","Date","Total","Completed","Ratio"
		,"Social","Health", "Overall"]]
	note_data = [["Day" , "Date" , "Notes"]]
	result_data = [["AVG Tasks" , "AVG Social" , "ANG Health" , "AVG Overall","Total Days"]]
	tasks_total = 0
	social_total = 0
	health_total = 0
	overall_total = 0
	for day in days:
		date = datetime.datetime.strptime(day.date[0:10] , '%Y-%m-%d')
		table_data.append(
			[calendar.day_name[date.weekday()],
			day.date[1:10],
			day.total_tasks,day.completed,day.get_tasks_ratio(),
			rating_scale(day.social_flag).name.replace("_" , " "),
			rating_scale(day.health_flag).name.replace("_" , " "),
			rating_scale(day.overall_flag).name.replace("_" , " ")])
		note_data.append([calendar.day_name[date.weekday()],day.date[1:10], day.note])
		tasks_total += day.get_tasks_ratio()
		social_total += day.social_flag
		health_total += day.health_flag
		overall_total += day.overall_flag

	counter = len(days)
	result_data.append([tasks_total/counter,
						rating_scale(int(round(social_total/counter))).name.replace("_"," ")
						,rating_scale(int(round(health_total/counter))).name.replace("_"," "),
						rating_scale(int(round(overall_total/counter))).name.replace("_"," "),
						counter])
	t1= Table(table_data,hAlign='LEFT')
	t1.setStyle(TableStyle([('BACKGROUND', (0, 0), (7, 0), colors.lightgrey),
						('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
						('BOX', (0,0), (-1,-1), 0.25, colors.black),]))
	t2= Table(note_data,hAlign='LEFT')
	t2.setStyle(TableStyle([('BACKGROUND', (0, 0), (2, 0), colors.lightgrey),
						('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
						('BOX', (0,0), (-1,-1), 0.25, colors.black)]))
	t3= Table(result_data,hAlign='LEFT')
	t3.setStyle(TableStyle([('BACKGROUND', (0, 0), (4, 0), colors.lightgrey),
						('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
						('BOX', (0,0), (-1,-1), 0.25, colors.black)]))
	elements = []
	elements.append(Paragraph(title_para,
	ParagraphStyle('title', fontSize=14)))
	elements.append(Spacer(width=0, height=10))

	elements.append(Paragraph("All Days Data:",
	ParagraphStyle('title', fontSize=11)))
	elements.append(Spacer(width=0, height=10))

	elements.append(t1)
	elements.append(Spacer(width=0, height=10))

	elements.append(Paragraph("All Days Notes:",
	ParagraphStyle('title', fontSize=11)))
	elements.append(Spacer(width=0, height=10))

	elements.append(t2)
	elements.append(Spacer(width=0, height=10))

	elements.append(Paragraph("Performance Result:",
	ParagraphStyle('title', fontSize=11)))
	elements.append(Spacer(width=0, height=10))

	elements.append(t3)
	c.build(elements)

def export_pdf_month(user_name):
	print(Fore.MAGENTA + "\n======= Export Month =======")
	month = read_positive_number("Enter month: " , 12)
	year = read_positive_number("Enter year: " , datetime.datetime.now().year)
	days = db.get_month_days(month,year)
	date = "%d-%02d" % (year, month)
	if len(days) == 0:
		print(Fore.WHITE + Back.RED + "\nThere is no stored data for " + date + "!" + Style.RESET_ALL + "\n" )
	else:
		path = os.path.join(os.path.expanduser("~"), "Desktop/", date + ".pdf")
		title = "%s - %d Performance Report for %s" % (calendar.month_abbr[month],year,user_name)
		generate_pdf(path,title,days)
		print("\n" + Back.BLUE + Fore.WHITE + " The requested report has been generated! Check out your desktop (•̀ᴗ•́)   " + Style.RESET_ALL )


def print_performance():
	print(Fore.MAGENTA + "\n======= Quick Report =======")
	days = db.get_all_days()
	if len(days) == 0:
		print(Fore.WHITE + Back.RED + "\nThere is no stored data!" + Style.RESET_ALL + "\n" )
	else:
		tasks_total = 0
		social_total = 0
		health_total = 0
		overall_total = 0
		for day in days:
			tasks_total += day.get_tasks_ratio()
			social_total += day.social_flag
			health_total += day.health_flag
			overall_total += day.overall_flag
		counter = len(days)
		print(Fore.CYAN + "Total Tasks Ratio: " + Fore.LIGHTBLUE_EX +str(tasks_total/counter))
		print(Fore.CYAN + "Social: " + Fore.LIGHTBLUE_EX +rating_scale(int(round(social_total/counter))).name.replace("_"," "))
		print(Fore.CYAN + "Health: " + Fore.LIGHTBLUE_EX +rating_scale(int(round(health_total/counter))).name.replace("_"," "))
		print(Fore.CYAN + "Overall: " + Fore.LIGHTBLUE_EX +rating_scale(int(round(overall_total/counter))).name.replace("_"," "))
		print(Fore.CYAN + "Number of days: " + Fore.LIGHTBLUE_EX +str(counter) + Style.RESET_ALL + "\n")

def export_pdf_all(user_name):
	print(Fore.MAGENTA + "\n======= Export All =======")
	days = db.get_all_days()
	if len(days) == 0:
		print(Fore.WHITE + Back.RED + "\nThere is no stored data!" + Style.RESET_ALL + "\n" )
	else:
		path = os.path.join(os.path.expanduser("~"), "Desktop/", "next_level_data.pdf")
		title = "Performance Report for %s" % user_name
		generate_pdf(path,title,days)
		print("\n" + Back.BLUE + Fore.WHITE + " The requested report has been generated! Check out your desktop (•̀ᴗ•́)   " + Style.RESET_ALL )

def view_day():
	print(Fore.MAGENTA + "\n======= View Day ======="+ Style.RESET_ALL)
	day = read_positive_number("Enter the day: ",30)
	month = read_positive_number("Enter the month: ",12)
	year = read_positive_number("Enter the year: ",datetime.datetime.now().year)
	date = "%d-%02d-%02d"%(year,month,day)
	day_information = db.get_day(date)
	if day_information != None:
		print(day_information)
	else:
		print(Fore.WHITE + Back.RED + "\nThere is no stored data for the entered day " + date + "!" + Style.RESET_ALL + "\n" )

if __name__ == '__main__':
	user = db.get_user_info()
	if user != None:
		welcome_text = '''
(\__/)
(•ㅅ•)
/ 　 づ %s ♥
WELCOME INTO YOUR NEXT LEVEL!
-----------------------------''' % user.name
		print(Fore.BLUE  + Style.BRIGHT + welcome_text + Style.RESET_ALL)
		print(Fore.CYAN + Style.BRIGHT + str(datetime.date.today()) + ", " +
		calendar.day_name[datetime.datetime.today().weekday()] + Style.RESET_ALL)
	else:
		user = set_up()


	day = db.get_day(datetime.datetime.today().strftime('%Y-%m-%d'))
	if day == None:
		print(Back.BLUE + Fore.YELLOW + Style.BRIGHT + "\nToday's Data, %s" % datetime.date.today() + Style.RESET_ALL)
		day = read_day_input(datetime.datetime.now())
		day.id = db.insert_day(day)

	else:
		print(Fore.CYAN +"AMAZING! You've filled out today's data ᕙ(`▽´)ᕗ" + Style.RESET_ALL)

	print(Fore.BLUE + Style.BRIGHT + "-----------------------------\n" + Style.RESET_ALL)
	utilities_var = 1
	while (utilities_var != 7):
		print()
		utilities_var = read_positive_number( Fore.MAGENTA  + Back.WHITE + Style.BRIGHT + "Select . . ." + Style.RESET_ALL
			+ Fore.YELLOW
			+ "\n1 : Edit configration.\n"
			+ "2 : View a day information.\n"
			+ "3 : Edit a day information.\n"
			+ "4 : Export a pdf for month.\n"
			+ "5 : Export a complete pdf.\n"
			+ "6 : Print a quick view of your performance till now.\n"
			+ "7 : Quit.\n" + Style.RESET_ALL, 7)
		if utilities_var == 1 : user = edit_configration(user)
		elif utilities_var == 2  : view_day()
		elif utilities_var == 3  : edit_day()
		elif utilities_var == 4  : export_pdf_month(user.name)
		elif utilities_var == 5  : export_pdf_all(user.name)
		elif utilities_var == 6  : print_performance()

	print(Fore.MAGENTA + Style.BRIGHT + "\n************************")
	print(" Have a Nice Day %s!" % user.name )
	print("************************\n"+ Style.RESET_ALL)