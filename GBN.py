import argparse
import socket
import time
import random

class GBN_Sender:
    """
    GBN Sender Class
    """
    def __init__(self, self_port, peer_address, peer_port, window_size, loss_type, n):
        self.self_port = self_port
        self.peer_address = peer_address
        self.peer_port = peer_port
        self.window_size = window_size
        self.loss_type = loss_type
        self.n = n
        self.base = 0
        self.next_seqnum = 0
        self.timer_running = False
        self.packet_loss_count = 0
        self.total_packets_sent = 0
        self.total_acks_received = 0
        self.socket1 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket1.bind(('localhost', self.self_port))
        self.socket1.settimeout(0.5)
        self.buffer = []
        self.start_time = 0
        self.expected_ack = 0

    def run(self):
        while True:
            message = input("node>")
            if message == 'exit':
                break
            elif message.startswith("send "):
                message = message.split("send ")[1]
                for i in message:
                    packet = self.make_packet(i.encode())
                    self.buffer.append(packet)
                    self.send_packet(packet)
                    self.total_packets_sent += 1
                    if self.next_seqnum < self.base + self.window_size:
                        if not self.timer_running:
                            self.start_timer()
                            self.start_time = time.time()
                        self.next_seqnum += 1
                    else:
                        print(f"Window full, waiting for ACKs...")
                    while self.expected_ack < self.total_packets_sent:
                        self.ack_rcvd()

            self.socket1.close()
            loss_rate = round(self.packet_loss_count / self.total_acks_received, 2) if self.total_acks_received!=0 else 0
            print(f"[Summary] {self.packet_loss_count}/{self.total_acks_received} packets discarded, loss rate = {loss_rate}%")

    def ack_rcvd(self):
        """
        Function to deal with the acknowledgements received
        """
        try:
            packet, address = self.socket1.recvfrom(1024)
            if not packet:
                print("no packets received")
            else:
                ack = self.extract_ack(packet)
                self.total_acks_received+=1
                if ack >= self.base:
                    if self.loss_or_not(ack):
                        print(f"ACK{ack} discarded")
                        self.packet_loss_count += 1
                    else:
                        print(f"[{time.time()}] ACK{ack} received, window moves to {ack + 1}")
                    self.base = ack + 1
                    if self.base == self.next_seqnum:
                        self.stop_timer()
                    else:
                        self.start_timer()
                        self.start_time = time.time()
                    self.buffer = self.buffer[ack-self.base:]
                    self.expected_ack+=1
                else:
                    print(f"[{time.time()}] ACK{ack} received, window moves to {ack + 1}")

        except socket.timeout:
            print(f"[{time.time()}] packet{self.base} timeout")
            self.timer_running = False
            self.next_seqnum = self.base
            for packet in self.buffer[1:]:
                self.send_packet(packet)
                self.next_seqnum += 1


    def make_packet(self, message):
        """
        Function to make packets to send to the peer port
        """
        seqnum = self.next_seqnum
        packet = b'%d:%s' % (seqnum, message)
        return packet

    def send_packet(self, packet):
        """
        Function to send the packet
        """
        print(f"[{time.time()}] packet{self.next_seqnum} {packet.decode()} sent")
        self.socket1.sendto(packet, (self.peer_address, self.peer_port))

    def extract_ack(self, packet):
        """
        Function to extract the acknowledgement received
        """
        return int(packet.decode().split(':')[1])

    def start_timer(self):
        """
        Function to keep track of the time when packet is sent and the timer is started
        """
        self.timer_running = True
        # print(f"[{time.time()}] timer started")

    def stop_timer(self):
        """
        Function to keep track of the time when the acknowledgement is received and the timer is stopped

        """
        self.timer_running = False
        # print(f"[{time.time()}] timer stopped")

    def loss_or_not(self, ack):
        """
        function to determine the loses
        """
        if self.loss_type == "deterministic":
            if ack != 0 and ack % self.n == 0:
                return True
            else:
                return False
        elif ack != 0 and self.loss_type == "probabilistic":
            if random.random() < self.n:
                return True
            else:
                return False



class GBN_Receiver:
    """
    GBN Receiver class
    """
    def __init__(self, self_port, peer_address, peer_port, window_size, loss_type, n):
        self.self_port = self_port
        self.peer_address = peer_address
        self.peer_port = peer_port
        self.window_size = window_size
        self.loss_type = loss_type
        self.n = n
        self.base = 0
        self.packets = [None] *self.window_size
        self.packet_loss_count = 0
        self.total_packets_count = 0
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(('localhost', self.self_port))
        self.socket.settimeout(10)
        self.buffer = []
        self.lost_packet_list= []
        self.last_packet_received = 0

   
    def run(self):
        """
        Main function the receive the packets and send acknowledgements
        """
        while True:
            try:
                packet, address = self.socket.recvfrom(1024)
                packet_num, packet_content = self.unpack_packet(packet)
                print(packet_num)
                self.total_packets_count+=1
                if self.loss_or_not(packet_num) and packet_num not in self.lost_packet_list:
                    print(f"Packet {packet_num} discarded")
                    self.packet_loss_count += 1
                    self.lost_packet_list.append(packet_num)
                else:
                    print(f"[{time.time()}] Packet{packet_num} {packet_content} received")
                    if packet_num in self.lost_packet_list:
                        self.lost_packet_list.remove(packet_num)
                    self.last_packet_received = packet_num


                if not self.lost_packet_list:
                    ack = self.make_ack(packet_num)
                    self.send_ack(ack)
                    print(f"[{time.time()}] ACK{packet_num} sent expecting packet{packet_num+1}")
                else:
                    ack = self.make_ack(self.lost_packet_list[0]-1)
                    self.send_ack(ack)
                    print(f"[{time.time()}] ACK{self.lost_packet_list[0]-1} sent expecting packet{self.lost_packet_list[0]}")
               
            except socket.timeout:
                # Timeout occurred, resend the ACK for the last packet
                ack = self.make_ack(self.last_packet_received)
                self.send_ack(ack)
                break
           
        self.socket.close()
        if self.total_packets_count != 0:
            loss_rate = round(self.packet_loss_count / self.total_packets_count, 2)
            print(f"[Summary] {self.packet_loss_count}/{self.total_packets_count} packets discarded, loss rate = {loss_rate}%")


    def make_ack(self, packet_num):
        """
        Function to make an acknowledgment
        """
        ack = f"ACK:{packet_num}"
        return ack.encode()

    def send_ack(self, ack):
        """
        Function to send an acknowledgment 
        """
        self.socket.sendto(ack, (self.peer_address, self.peer_port))

    def unpack_packet(self, packet):
        """
        To decode the packets received
        """
        packet_num, packet_content = packet.decode().split(':')
        packet_num = int(packet_num)
        return packet_num, packet_content

    def loss_or_not(self, ack):
        """
        function to determine the loses
        """
        if self.loss_type == "deterministic":
            if ack != 0 and ack % self.n == 0:
                return True
            else:
                return False
        elif ack != 0 and self.loss_type == "probabilistic":
            if random.random() < self.n:
                return True
            else:
                return False
   



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='GBN Sender')
    parser.add_argument('self_port', type=int, help='Sender port number')
    peer_ip = 'localhost'
    parser.add_argument('peer_port', type=int, help='Receiver port number')
    parser.add_argument('window_size', type=int, help='Window size')
    parser.add_argument('--d', type=int, required=False, help='Packet loss parameter for deterministic loss')
    parser.add_argument('--p', type=float,required=False, help='Packet loss probability for probabilistic loss')
    args = parser.parse_args()
    if args.d:
        loss = "deterministic"
        n = args.d
    else:
        loss = "probabilistic"
        n = args.p
   
    receiver = GBN_Receiver(args.self_port, peer_ip, args.peer_port, args.window_size, loss, n)
    receiver.run()
    sender = GBN_Sender(args.self_port, peer_ip, args.peer_port, args.window_size, loss, n)
    sender.run()

