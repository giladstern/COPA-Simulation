from Receiver import Receiver
from Sender import Sender
from collections import deque


class Simulator:
    def __init__(self, buff_size, serve_per_timestep, ttl, sender_num, long_time, path):
        self.log = open(path, "w")
        self.dest = Receiver(self, buff_size, serve_per_timestep)
        self.senders = [Sender(self, self.dest, long_time, ttl, i) for i in range(sender_num)]
        self.messages = deque()
        self.ttl = ttl
        self.time = 0

    def add_sender(self, sender):
        self.senders.append(sender)

    def timestep(self):
        self.time += 1
        for i in range(len(self.messages)):
            message = self.messages.popleft()
            message.timestep()
            if message.ttl > 0:
                self.messages.append(message)
        for sender in self.senders:
            sender.timestep()
        self.dest.timestep()

        if not self.time % 100:
            print(self.senders[0].cwnd - self.senders[1].cwnd, self.senders[0].cwnd + self.senders[1].cwnd)

    def send_message(self, message):
        message.ttl = self.ttl
        self.messages.append(message)

    def log_write(self, str):
        self.log.write(str)


sim = Simulator(1000, 2, 50, 2, 5000, "logfile")

for i in range(10000):
    sim.timestep()

sim.log.close()
