import socket
import random
import json
data = { 
      "jsonrpc": "2.0",
      "method": "put_avg_data",
      "params": {
        "name": "ws-msg",
        "value": random.randint(5,400),
        "unit":  "Count"
      },  
      "id": 1
}
 
client_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
client_socket.connect('/var/tmp/ext-sauron.sock')
i = 0 
while 1:
  try:
    client_socket.send(json.dumps(data) + '\n')
    i += 1
    print "RECIEVED:"
    print client_socket.recv(4096)
  except KeyboardInterrupt:
    client_socket.close()
    print "connection closed"
    print 'send %i values' % (i) 

