from Message import Message
from collections import deque


class Sender:
    def __init__(self, simulator, dest, long_time, ttl):
        self.ttl = ttl
        self.cwnd = 100
        self.RTT_st = 2 * ttl
        self.RTT_min = 2 * ttl
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
        self.srtt = 2 * ttl
        self.time = 1
        self.acks_till_close = 1
        self.prev_cwnd = 1
        # TODO: Decide if we want timeouts

    def send_message(self):
        message = Message(self, self.dest, self.ack_num)
        self.ack_num += 1
        self.simulator.send_message(message)

    def default_timestep(self):
        self.partial_send += 2 * self.cwnd / self.RTT_st
        num_messages = int(self.partial_send)

        for i in range(num_messages):
            self.send_message()

        self.partial_send -= num_messages

    def competitive_timestep(self):
        pass

    def timestep(self):
        while len(self.last_rtts) > 0 and self.last_rtts[0].received < self.time - self.long_time:
            self.last_rtts.popleft()

        filtered = filter(lambda m: m.received >= self.time - self.srtt / 2, self.last_rtts)
        self.RTT_st = min(map(lambda m: m.time_alive, filtered), default=2 * self.ttl)
        self.RTT_min = min(map(lambda m: m.time_alive, self.last_rtts), default=2 * self.ttl)

        if self.competitive:
            self.competitive_timestep()
        else:
            self.default_timestep()
        self.time += 1

        print(self.cwnd)

    def receive(self, message):
        message.received = self.time
        self.last_rtts.append(message)

        # Update the RTT statistics.
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
            self.RTT_min = min(self.RTT_min, message.time_alive)

        # # This whole block is for updating v.
        # if self.acks_till_close > 0:
        #     self.acks_till_close -= 1
        #
        #     if self.acks_till_close == 0:
        #         if len(self.last_directions) == 3:
        #             self.last_directions.pop(0)
        #
        #         if self.cwnd > self.prev_cwnd:
        #             direction = 1
        #         else:
        #             direction = -1
        #         self.last_directions.append(direction)
        #
        #         total = sum(self.last_directions)
        #
        #         if total == 3 or total == -3:
        #             self.v *= 2
        #         else:
        #             self.v = 1
        #
        #         self.prev_cwnd = self.cwnd
        #         self.acks_till_close = int(self.cwnd)


        # Updating cwnd.
        d_q = self.RTT_st - self.RTT_min

        if d_q:
            lam_t = 1 / (self.delta * d_q)
            lam = self.cwnd / self.RTT_st

            if lam <= lam_t:
                self.cwnd += self.v / (self.delta * self.cwnd)
            else:
                self.cwnd -= self.v / (self.delta * self.cwnd)
        else:
            self.cwnd += self.v / (self.delta * self.cwnd)
