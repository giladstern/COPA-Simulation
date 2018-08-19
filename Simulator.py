from Receiver import Receiver
from Sender import Sender
from collections import deque


class Simulator:
    def __init__(self, buff_size, serve_per_timestep, ttl, sender_num, long_time):
        self.dest = Receiver(self, buff_size, serve_per_timestep)
        self.senders = [Sender(self, self.dest, long_time, ttl) for i in range(sender_num)]
        self.messages = deque()
        self.ttl = ttl

    def add_sender(self, sender):
        self.senders.append(sender)

    def timestep(self):
        for i in range(len(self.messages)):
            message = self.messages.popleft()
            message.timestep()
            if message.ttl > 0:
                self.messages.append(message)
        for sender in self.senders:
            sender.timestep()
        self.dest.timestep()

    def send_message(self, message):
        message.ttl = self.ttl
        self.messages.append(message)


sim = Simulator(1000, 2, 50, 1, 5000)

for i in range(500000):
    sim.timestep()
