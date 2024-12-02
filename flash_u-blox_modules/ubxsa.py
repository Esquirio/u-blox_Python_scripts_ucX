import time
import sys;

time_delay = 0.1

class UBXSerialAdapter: 
	def __init__(self, stream):
		self._stream = stream
		# self._stream.flushInput()
	
	def get_stream(self):
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

	def send_command(self, command):
		#Send command
		self.writeline(command)

	def wait_for_startup(self):
		r = self.read()
		#Read response until STARTUP received
		while (str.find(r.decode(),"+STARTUP") < 0):
			r = r + self.read()
		return r.decode()[r.decode().find("+STARTUP"):]

	def wait_for_response(self, response):
		r = self.readline()
		#Read response until response or ERROR received
		while (str.find(r.decode(),response) < 0 and str.find(r.decode(),"ERROR") <0):
			r = r + self.readline()
		
		if (str.find(r.decode(),"ERROR") >= 0):
			print("ERROR");
			sys.stdout.flush()
			return -1
		return r.decode()
		
	def enter_command_mode(self, esc="+++", timeout=1.1):
		time.sleep(timeout)
		self.write(esc.encode())
		time.sleep(timeout)
		
	def reset_device(self):
		self.send_command("AT+UFACTORY")
		self.send_command("AT+CPWROFF")
		self.waitForStartup()

	def enter_data_mode(self):
		self.send_command("ATO1")
