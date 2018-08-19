from Message import Message
from collections import deque


class Sender:
    def __init__(self, simulator, dest, long_time):
        self.cwnd = 1
        self.RTT_st = 1
        self.RTT_min = 1
        self.v = 1
        self.last_rtts = deque()
        self.last_directions = []
        self.delta = 0.5
        self.dest = dest
        self.rate = 1
        self.ack_num = 1
        self.simulator = simulator
        self.competitive = False
        self.messages_in_air = 0
        self.expected_ack = 1
        self.long_time = long_time
        self.partial_send = 1
        self.srtt = 0
        self.time = 1
        # TODO: Decide if we want timeouts

    def send_message(self):
        message = Message(self, self.dest, self.ack_num)
        self.ack_num += 1
        self.simulator.send_message(message)

    def default_timestep(self):
        self.RTT_st = min(filter(lambda m: m.received >= self.time - self.srtt / 2, self.last_rtts)
                          , key=lambda m: m.time_alive
                          , default=0)
        self.RTT_min = min(self.last_rtts, key=lambda m: m.time_alive, default=0)

    def competitive_timestep(self):
        pass

    def timestep(self):
        while len(self.last_rtts) > 0 and self.last_rtts[0].received < self.time - self.long_time:
            self.last_rtts.pop()
        self.RTT_st = min(filter(lambda m: m.received >= self.time - self.srtt / 2, self.last_rtts)
                          , key=lambda m: m.time_alive
                          , default=0)
        self.RTT_min = min(self.last_rtts, key=lambda m: m.time_alive, default=0)

        if not self.competitive:
            self.default_timestep()
        else:
            self.competitive_timestep()
        self.time += 1

    def receive(self, message):
        message.received = self.time

        if self.srtt == 0:
            self.srtt = message.time_alive
        else:
            self.srtt = 0.1 * message.time_alive + 0.9 * self.srtt

        if self.RTT_st == 0:
            self.RTT_st = message.time_alive
        else:
            self.RTT_st = min(self.RTT_st, message.time_alive)

        if self.RTT_min == 0:
            self.RTT_min = message.time_alive
        else:
            self.RTT_min = min(self.RTT_st, message.time_alive)
