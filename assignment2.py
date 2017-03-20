import sys
import socketserver
import socket, threading
import time

global inc_hexdump
inc_hexdump = ""
global inc_bytescollected 
inc_bytescollected = 0
global rec_hexdump
rec_hexdump = ""
global rec_bytescollected
rec_bytescollected = 0

def logOptions(incoming, data, option, nAuto):
	# -raw option
	if option == 1:
		datalist = data.split("\n")
		del datalist[len(datalist)-1]
		for element in datalist:
			if incoming:
				sys.stdout.write("---> " + element + "\n")
			else:
				sys.stdout.write("<--- " + element + "\n")
	
	# -strip option
	elif option == 2:
		datalist = data.split("\n")
		del datalist[len(datalist)-1]
		# Replace non-printable characters with "."
		for string in datalist:
			for i in range(len(string)):
				if ord(data[i]) < 32:
					newData = list(string)
					newData[i] = "."
					string = "".join(newData)
			if incoming:
				sys.stdout.write("---> " + string + "\n")
			else:
				sys.stdout.write("<--- " + string + "\n")
	
	# -hex option	
	elif option == 3:
		# Replace non-printable characters with "."
		for i in range(len(data)):
			if ord(data[i]) < 32:
				newData = list(data)
				newData[i] = "."
				data = "".join(newData)
		
		# Print 16 bytes for each line in hex		
		if incoming:
			global inc_hexdump
			global inc_bytescollected
			inc_hexdump += data
			while len(inc_hexdump) >= 16:
				sys.stdout.write("\n---> ")
				sys.stdout.flush()
				
				# Counter for bytes already logged
				sys.stdout.write("{:08x}".format(inc_bytescollected) + " ")
				sys.stdout.flush()
			
				for i in inc_hexdump[:16]:
					sys.stdout.write(hex(ord(i)).replace("0x", "") + " ")
					sys.stdout.flush()
				
				# Print the original data	
				sys.stdout.write(" |" + inc_hexdump[:16] + "|")
				sys.stdout.flush()
				
				# Increment the counter by the number of bytes collected so far	
				inc_bytescollected += 16
				# Remove the collected characters
				inc_hexdump = inc_hexdump[16:]
				
			
		else:
			global rec_hexdump
			global rec_bytescollected
			rec_hexdump += data
			while len(rec_hexdump) >= 16:
				sys.stdout.write("\n<--- ")
				sys.stdout.flush()
				
				# Counter for bytes already logged
				sys.stdout.write("{:08x}".format(rec_bytescollected) + " ")
				sys.stdout.flush()
			
				for i in rec_hexdump[:16]:
					sys.stdout.write(hex(ord(i)).replace("0x", "") + " ")
					sys.stdout.flush()
				
				# Print the original data	
				sys.stdout.write(" |" + rec_hexdump[:16] + "|")
				sys.stdout.flush()
				
				# Increment the counter by the number of bytes collected so far	
				rec_bytescollected += 16
				# Remove the collected characters
				rec_hexdump = rec_hexdump[16:]
	
	# -autoN option	
	elif option == 4:
		# Replace backslash, tab, newline, and carriage return
		for i in range(len(data)):
			if ord(data[i]) == 92:
				newData = list(data)
				newData[i] = "\\"
				data = "".join(newData)
			elif ord(data[i]) == 9:
				newData = list(data)
				newData[i] = "\t"
				data = "".join(newData)
			elif ord(data[i]) == 10:
				newData = list(data)
				newData[i] = "\n"
				data = "".join(newData)
			elif ord(data[i]) == 13:
				newData = list(data)
				newData[i] = "\r"
				data = "".join(newData)
		
		if incoming:
			while len(data) > 0:	
				sys.stdout.write("\n---> ")
				sys.stdout.flush()
				
				sys.stdout.write(repr(data[:nAuto]).strip("'"))
				sys.stdout.flush()
				data = data[nAuto:]
				
		else:
			while len(data) > 0:	
				sys.stdout.write("\n<--- ")
				sys.stdout.flush()
				
				sys.stdout.write(repr(data[:nAuto]).strip("'"))
				sys.stdout.flush()
				data = data[nAuto:]
		

# Handler for the TCP Server
class TCPRequestHandler(socketserver.BaseRequestHandler):
	option = 0
	nAuto = 0
	#Connect to the server
	if len(sys.argv) == 4:
		pass
	elif len(sys.argv) == 5:
		if sys.argv[1] == "-raw":
			option = 1
		elif sys.argv[1] == "-strip":
			option = 2
		elif sys.argv[1] == "-hex":
			option = 3
		elif sys.argv[1].startswith("-auto"):
			option = 4
			nAuto = int(sys.argv[1].replace("-auto", ""))
			
	BUFFER_SIZE = 4096
	clientList = []
	serverList = []
	
	def handle(self):
		self.clientList.append(self.request)
		serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		try:
			if len(sys.argv) == 4:
				serverSocket.connect((sys.argv[2], int(sys.argv[3])))
			elif len(sys.argv) == 5:
				serverSocket.connect((sys.argv[3], int(sys.argv[4])))
		except ConnectionRefusedError:
			serverSocket = self.serverList[0]
			
		self.serverList.append(serverSocket)
		
		# Display new connection
		if len(sys.argv) == 4:	
			sys.stdout.write("Port logger running: srcPort=" + sys.argv[1] + " host=" + sys.argv[2] + " dstPort=" + sys.argv[3] + "\n")
		else:
			sys.stdout.write("Port logger running: srcPort=" + sys.argv[2] + " host=" + sys.argv[3] + " dstPort=" + sys.argv[4] + "\n")
		sys.stdout.write("New connection: ")
		sys.stdout.write(time.strftime("%Y %m %d %H:%M:%S"))
		sys.stdout.write(", from "+ str(self.request.getpeername()[0]) + "\n")
			
		while True:
			data = None
			
			i = 0
			while i < len(self.clientList):
				try:
					#Receive data from client
					data = self.clientList[i].recv(self.BUFFER_SIZE, socket.MSG_DONTWAIT)
					
					if i >= len(self.clientList):
						break
					
					if len(data) == self.BUFFER_SIZE:
						while True:
							try:
								data += self.clientList[i].recv(self.BUFFER_SIZE, socket.MSG_DONTWAIT)
							except:
								break
					#Client disconnected
					elif len(data) == 0 and self.clientList[i] == self.request:
						break
					#Send to server
					while len(self.clientList) != len(self.serverList):
						pass
					self.serverList[i].sendall(data)
					
					try:
						data = data.decode('utf-8')
					except UnicodeDecodeError:
						data = data.decode('latin-1')
					logOptions(True, data, self.option, self.nAuto)
				
				#No data to be received
				except BlockingIOError:
					pass
				i += 1
			
			while len(self.clientList) != len(self.serverList):
				pass
				
			for i in range(len(self.serverList)):
				try:
					#Receive data from server
					data = self.serverList[i].recv(self.BUFFER_SIZE, socket.MSG_DONTWAIT)
					if len(data) == self.BUFFER_SIZE:
						while True:
							try:
								data += self.serverList[i].recv(self.BUFFER_SIZE, socket.MSG_DONTWAIT)
							except:
								break	
					#Send data to client
					if len(self.serverList) > 1:
						if self.serverList[0] == self.serverList[1]:
							for j in range(len(self.clientList)):
								self.clientList[j].sendall(data)
						else:
							self.clientList[i].sendall(data)
					else:
						self.clientList[i].sendall(data)
						
					try:
						data = data.decode('utf-8')
					except UnicodeDecodeError:
						data = data.decode('latin-1')
					logOptions(False, data, self.option, self.nAuto)
			
				#No data to be received	
				except BlockingIOError:
					pass
		
		self.server.shutdown()
		self.server.server_close()

if __name__ == "__main__":
	if len(sys.argv) == 4:
		HOST, PORT = "localhost", int(sys.argv[1])
	elif len(sys.argv) == 5:
		HOST, PORT = "localhost", int(sys.argv[2])
	socketserver.ThreadingTCPServer.allow_reuse_address = True
	server = socketserver.ThreadingTCPServer((HOST,PORT), TCPRequestHandler)
	server.serve_forever()
	
				
	
	
