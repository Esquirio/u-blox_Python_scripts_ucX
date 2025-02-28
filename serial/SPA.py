import re
import time
import string
import sys;

class SPA: 
	def __init__(self, stream):
		self._stream = stream
		self._stream.flushInput()
	
	def getStream(self):
		return self._stream
	
	def read(self, size=1):
		return self._stream.read(size)
	
	def readline(self):
		r = self._stream.readline().strip()
		return r
			
	def write(self, data):
		return self._stream.write(data)
	
	def writeline(self, line):
		self._stream.write(line.encode() + b'\r')
		self._stream.flush()

	def command(self, command):
		#Send command
		self.writeline(command)
		
		#Search the response for the sent command to be sure that it has been sent before we proceed
		r = self.readline()		   
		
		#Read response until OK or ERROR received
		while (str.find(r.decode(),"OK") < 0 and str.find(r.decode(),"ERROR") <0):
			r = r + self.readline()
		
		if (str.find(r.decode(),"ERROR") >= 0):
			# print("ERROR");
			sys.stdout.flush()
			return -1

		return r

	def waitForStartup(self):
		r = self.read()				  
		#Read response until STARTUP received
		while (str.find(r.decode(),"+STARTUP") < 0):
			r = r + self.read()
		return r

	
	def waitForResponse(self, response):
		r = self.readline()
		while (str.find(r.decode(),response) < 0):
			r = r + self.readline()
		return r
		
	def enterCommandMode(self, esc="+++", timeout=1.1):
		time.sleep(timeout)
		self.write(esc.encode())
		time.sleep(timeout)
		
	def resetDevice(self):
		self.command("AT+UFACTORY")
		self.command("AT+CPWROFF")
		self.waitForStartup()

	def enterDataMode(self):
		self.command("ATO1")

