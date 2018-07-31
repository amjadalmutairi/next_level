import sqlite3
import os
from user import User
import base64
from day import Day

def get_db_connection():
	return sqlite3.connect("next_level.db")

def create_db():
	db_connection = get_db_connection()
	cursor = db_connection.cursor()
	q = ""
	with open('schema.sql', 'r') as f:
		q = f.read()
		f.close()
	cursor.execute("PRAGMA foreign_keys = ON")
	cursor.executescript(q)
	#insert domain values
	rating_scales = {1:"EXCELLENT" , 2 : "VERY GOOD" , 3 : "GOOD" , 4 : "FAIR" , 5 : "POOR" }
	for value , text in  rating_scales.items():
		q = '''INSERT INTO rating_scales (text,value) VALUES (?,?);'''
		cursor.execute(q, (text,value))
	db_connection.commit()
	db_connection.close()

def insert_new_user(user):
	db_connection = get_db_connection()
	cursor = db_connection.cursor()
	q = ''' INSERT INTO user (name,email,password,receive_email) VALUES (?,?,?,?);'''
	if(user.receive_email == 1):
		cursor.execute(q,(user.name,user.email,base64.b64encode(user.password.encode('ascii')),user.receive_email))
	else:
		cursor.execute(q,(user.name,user.email,user.password,user.receive_email))
	db_connection.commit()
	db_connection.close()
	return cursor.lastrowid

def get_user_info():
	if  os.path.isfile("next_level.db"):
		db_connection = get_db_connection()
		cursor = db_connection.cursor()
		q = ''' SELECT * FROM user'''
		user = cursor.execute(q).fetchone()
		if user != None:
			if user[3] != None:
				user = User(user[1],user[2],base64.b64decode(user[3]),user[4],user[0])
			else:
				user = User(user[1],None,None,user[4],user[0])
			db_connection.close()
			return user
		else:
		 db_connection.close()
		 return None;
	else:
		return None;

def insert_day(day):
	db_connection = get_db_connection()
	cursor = db_connection.cursor()
	q = ''' INSERT INTO day (user_id, date, total, completed, social, health, overall, note)
	VALUES (?,?,?,?,?,?,?,?) '''
	cursor.execute(q,(day.user_id,day.date,day.total_tasks,day.completed,day.social_flag,
	day.health_flag,day.overall_flag,day.note))
	db_connection.commit()
	db_connection.close()
	return cursor.lastrowid

def update_user(user):
	db_connection = get_db_connection()
	cursor = db_connection.cursor()
	q = "UPDATE user SET name=? , email=?, password=?, receive_email=? WHERE id=?"
	if user.email != None:
		cursor.execute(q,(user.name,user.email,base64.b64encode(user.password.encode('ascii')),user.receive_email,user.id))
	else:
		cursor.execute(q,(user.name,None,None,user.receive_email,user.id))
	db_connection.commit()
	db_connection.close()

def update_day(day):
	db_connection = get_db_connection()
	cursor = db_connection.cursor()
	q = "UPDATE day SET total=?, completed=?, social=?, health=?, overall=?, note=? WHERE id=?"
	cursor.execute(q,(day.total_tasks, day.completed, day.social_flag, day.health_flag, day.overall_flag, day.note,day.id ))
	db_connection.commit()
	db_connection.close()

def get_day(date):
	db_connection = get_db_connection()
	cursor = db_connection.cursor()
	q = ''' SELECT * FROM day WHERE substr(date, 1, 10) = ? '''
	result = cursor.execute(q,(date,)).fetchone()
	if result != None:
		if len(result) > 8:
			day = Day(result[1],result[2],result[3],result[4],result[5],result[6],result[7],result[8],result[0])
		else:
			day = Day(result[1],result[2],result[3],result[4],result[5],result[6],result[7],None,result[0])
		db_connection.close()
		return day
	else:
		db_connection.close()
		return None

def get_month_days(month,year):
	db_connection = get_db_connection()
	cursor = db_connection.cursor()
	q = '''SELECT * FROM day WHERE date BETWEEN \'%d-%02d-00\'  AND \'%d-%02d-32\''''%(year,month,year,month)
	cursor.execute(q)
	days = cursor.fetchall()
	days_list = []
	for day in days:
		d = Day(day[1],day[2],day[3],day[4],day[5],day[6],day[7],day[8],day[0])
		days_list.append(d)
	db_connection.close()
	return days_list

def get_all_days():
	db_connection = get_db_connection()
	cursor = db_connection.cursor()
	q = '''SELECT * FROM day ORDER BY date ASC '''
	cursor.execute(q)
	days = cursor.fetchall()
	days_list = []
	for day in days:
		d = Day(day[1],day[2],day[3],day[4],day[5],day[6],day[7],day[8],day[0])
		days_list.append(d)
	db_connection.close()
	return days_list

def insert_report(user,y,m,hasSent):
	db_connection = get_db_connection()
	cursor = db_connection.cursor()
	q = ''' INSERT INTO report (user_id,month,year,has_sent,email) VALUES (?,?,?,?,?);'''
	cursor.execute(q,(user.id,m,y,hasSent,user.email))
	db_connection.commit()
	db_connection.close()
