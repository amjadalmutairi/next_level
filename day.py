from colorama import Fore, Back, Style
from enum import Enum

class rating_scale(Enum):
	EXCELLENT = 1
	VERY_GOOD = 2
	GOOD = 3
	FAIR = 4
	POOR = 5

class Day(object):
	def __init__(self,user_id, date,total_tasks,completed,social_flag,health_flag,overall_flag,note,id=None):
		self.id = id
		self.user_id = user_id
		self.date = date
		self.total_tasks = total_tasks
		self.completed = completed
		self.social_flag = social_flag
		self.health_flag = health_flag
		self.overall_flag = overall_flag
		self.note = note

	def get_tasks_ratio(self):
		if self.completed == 0:
			return 0
		else:
			return round(self.completed/self.total_tasks,2)

	def __str__(self):
		return (( "\n" + Style.BRIGHT + Fore.BLUE + Back.WHITE  + self.date[0:10] + ":" + Style.RESET_ALL)
		+"\n" +  (Style.BRIGHT + Fore.CYAN + "Total Tasks: " + Fore.MAGENTA +  str(self.total_tasks))
		+"\n" +  (Fore.CYAN + "Completed Tasks: " + Fore.MAGENTA + str(self.completed))
		+"\n" +  (Fore.CYAN + "Social Activity: " + Fore.MAGENTA + rating_scale(self.social_flag).name.replace("_" , " "))
		+"\n" + (Fore.CYAN + "Health Activity: " + Fore.MAGENTA + rating_scale(self.health_flag).name.replace("_" , " "))
		+"\n" +  (Fore.CYAN + "Overall Performance: "+ Fore.MAGENTA  + rating_scale(self.overall_flag).name.replace("_" , " "))
		+"\n" +  (Fore.CYAN + "Your Note: " + Fore.MAGENTA + self.note  + "\n" + Style.RESET_ALL))

