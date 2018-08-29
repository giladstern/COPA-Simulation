from Receiver import Receiver
from Sender import Sender
from collections import deque
import matplotlib.pyplot as plt
import numpy as np


class Simulator:
    def __init__(self, buff_size, serve_per_timestep, ttl, sender_num, long_time, path):
        self.log = open(path, "w")
        self.dest = Receiver(self, buff_size, serve_per_timestep)
        self.senders = [Sender(self, self.dest, long_time, ttl, i, ttl/sender_num) for i in range(sender_num)]
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

        # if not self.time % 100:
        #     print(self.senders[0].cwnd - self.senders[1].cwnd, self.senders[0].cwnd + self.senders[1].cwnd)

    def send_message(self, message):
        message.ttl = self.ttl
        self.messages.append(message)

    def log_write(self, string):
        self.log.write(string)


for i in range(1):
    time = 100000
    buff = 1000
    serve = 2
    ttl = 50
    num_senders = 2
    long = 5000

    sim = Simulator(buff, serve, ttl, num_senders, long, "logfile")

    for i in range(time):
        sim.timestep()

    sim.log.close()

    y = [i for i in range(1, time + 1)]

    for sender in sim.senders:
        plt.plot(y, sender.plot, label="Sender " + str(sender.id))

    x = sum(np.array(sender.plot) for sender in sim.senders)
    plt.plot(y, x, label="Sum")

    x_max = np.array([max(sender.plot[i] for sender in sim.senders) for i in range(time)])
    x_min = np.array([min(sender.plot[i] for sender in sim.senders) for i in range(time)])
    plt.plot(y, x_max - x_min, label="Max Difference")

    plt.legend()
    plt.show()

    print(x_max[-1]-x_min[-1])
