
class User(object):
	def __init__(self,name,email,password,receive_email,id=None):
		self.id = id
		self.name = name
		self.email = email
		self.password = password
		self.receive_email  = receive_email