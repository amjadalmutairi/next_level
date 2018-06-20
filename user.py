
class User(object):
	def __init__(self,name,email,password,id=None):
		self.id = id
		self.name = name
		self.email = email
		self.password = password