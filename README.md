# GoBack-N-Protocol
In this  project , you will emulate the operation of a link layer and network layer protocol in a small computer network. You will start several nodes so that they can send packets to each other as if there are links between them. Running as an independent node, your program should implement a simple version of GoBack-N Protocol Link Layer.




Python script for implementing a Go-Back-N (GBN) protocol. The GBN protocol is a type of sliding window protocol used for reliable communication in computer networks. The sender is implemented as a class called GBN_Sender, which takes command line arguments for the sender's port number (self_port), receiver's address (peer_address), receiver's port number (peer_port), window size (window_size), type of packet loss (loss_type), and a loss parameter (n) that depends on the type of packet loss and similarly Receiver is in the GBN_Receiver class.

The GBN_Sender class has several methods:

__init__(self, self_port, peer_address, peer_port, window_size, loss_type, n): This is the constructor method that initializes the sender object with the provided parameters. It creates a UDP socket and binds it to the sender's address and port, sets the timeout for the socket, and initializes various variables such as base, next_seqnum, timer_running, packet_loss_count, total_packets_sent, total_acks_received, buffer, and start_time.

run(self): This method runs an infinite loop to receive input from the user as messages to be sent to the receiver. It handles the logic for sending packets, starting and stopping the timer, receiving acknowledgments (ACKs), and detecting packet loss. It also calculates the packet loss rate based on the total number of ACKs received and the number of packets lost.

ack_rcvd(self): This method receives ACK packets from the receiver, extracts the ACK number, and updates the sender's variables and buffer accordingly. It also handles the case when a timeout occurs by resending packets that have not been acknowledged.

make_packet(self, message): This method takes a message as input, adds a sequence number to it, and returns a packet ready to be sent.

send_packet(self, packet): This method sends a packet to the receiver.

extract_ack(self, packet): This method extracts the ACK number from an ACK packet.

start_timer(self): This method starts the timer.

stop_timer(self): This method stops the timer.

loss_or_not(self, ack): This method determines whether a packet should be lost based on the type of loss (deterministic or probabilistic) and the value of the loss parameter (n).


Similarly we have the same formart for The GBN Receiver Class:

GBN_Receiver class, which represents the GBN receiver. It has methods for initializing the receiver, running the main receive loop, making and sending acknowledgements, unpacking received packets, and determining packet losses.

run() method, which is the main function that receives packets, sends acknowledgements, handles packet losses, and calculates loss rate.

make_ack() and send_ack() methods, which are used to create and send acknowledgements, respectively.

unpack_packet() method, which is used to decode the received packets.

loss_or_not() method, which is used to determine if a packet should be discarded based on the specified loss type and its corresponding parameter (n or p).



The script also includes command line argument parsing using the argparse module, which allows the user to provide input for various parameters such as the sender's port number, receiver's port number, window size, and type of packet loss. If the --d option is provided, the script sets the loss type to "deterministic" and uses the value of args.d as the loss parameter n. Otherwise, it sets the loss type to "probabilistic" and uses the value of args.p as the loss probability n.
The GBN_Sender and GBN_Receiver class  is then instantiated with the provided parameters, and the run() method is called to start the sender's operation.



Steps For Implementation

1. Run the python file using  python gbnnode.py <self-port> <peer-port> <window-size> [ -d <value-of-n> | -p <value-of-p> ].
   for eg: python gbnnode.py 6000 6001 10 --d 4 in one terminal and run python gbnode.py 6001 6000 10 --d 4 in another to act as 
   an receiver.
2. The program waits for a set amount of time to check if it receives any messages , wait for the "node>" message to come   up in the terminal.
   After you got the "node>" message go and start the receiver node using  python gbnnode.py 6001 6000 10 --d 4  before inputting any Values
   to the sender node . Once the receiver is started input the message to the sender immediately. for eg: send abcdefghijk.
   Make sure you add "send" keyword before sending anything because that is the accepted format.
3. You should be able to see the status messages in the respective terminals as given in the description.
4. PS: I have used localhost to test the code , you could change the ip_address to the google cloud ubuntu instance you are testing your code in as mentioned in the problem also you could use the port numbers according to your needs.
