from Message import Message
from collections import deque


class Sender:
    def __init__(self, simulator, dest, long_time, ttl, id, cwnd):
        self.id = id
        self.ttl = ttl
        self.cwnd = cwnd
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
        self.long_time = long_time
        self.partial_send = 1
        self.srtt = 2 * ttl
        self.time = 1
        self.last_in_window = 1
        self.prev_cwnd = self.cwnd
        self.RTT_max = 2 * ttl
        self.dupack = 0
        self.expected_ack = 1
        # TODO: Decide if we want timeouts
        self.d = 1
        self.plot = []

    def send_message(self):
        message = Message(self, self.dest, self.ack_num, self.prev_cwnd)
        self.ack_num += 1
        self.simulator.send_message(message)

    def default_timestep(self):
        self.partial_send += 2 * self.cwnd / self.RTT_st
        num_messages = int(self.partial_send)

        for i in range(num_messages):
            self.send_message()

        self.partial_send -= num_messages

    def competitive_timestep(self):
        for i in range(max(0, int(self.cwnd) - self.messages_in_air)):
            self.send_message()

    def timestep(self):
        self.messages_in_air = self.ack_num - self.expected_ack

        while len(self.last_rtts) > 0 and self.last_rtts[0].received < self.time - self.long_time:
            self.last_rtts.popleft()

        # TODO: What about messages "ignored" in competitive mode?
        # filtered_st = filter(lambda m: m.received >= self.time - self.srtt / 2, self.last_rtts)
        # filtered_max = filter(lambda m: m.received >= self.time - 4 * self.srtt, self.last_rtts)
        # self.RTT_st = min(map(lambda m: m.time_alive, filtered_st), default=self.RTT_st)
        # self.RTT_min = min(map(lambda m: m.time_alive, self.last_rtts), default=self.RTT_min)
        # self.RTT_max = max(map(lambda m: m.time_alive, filtered_max), default=self.RTT_max)

        if self.last_rtts:
            self.RTT_st = self.RTT_min = self.RTT_max = self.last_rtts[-1].time_alive

        long_delay = True
        for message in self.last_rtts:
            rtt = message.time_alive
            if long_delay and message.received >= self.time - 5 * self.srtt and message.nearly_empty:
                long_delay = False
            if rtt < self.RTT_min:
                self.RTT_min = rtt
            if message.received >= self.time - self.srtt / 2 and rtt < self.RTT_st:
                self.RTT_st = rtt
            if message.received >= self.time - 4 * self.srtt and rtt > self.RTT_st:
                self.RTT_max = rtt

        # Here we are just waiting for stabilization.
        if self.time >= 5000:
            if long_delay:
                self.competitive = True
                self.log_write("Competitive in time: " + str(self.time))
            else:
                self.competitive = False

        if self.competitive:
            self.competitive_timestep()
        else:
            self.default_timestep()

        self.plot.append(self.cwnd)
        self.time += 1

    def receive(self, message):
        message.received = self.time
        self.last_rtts.append(message)

        # Update the RTT statistics.
        self.srtt = 0.1 * message.time_alive + 0.9 * self.srtt
        self.RTT_st = min(self.RTT_st, message.time_alive)
        self.RTT_min = min(self.RTT_min, message.time_alive)
        self.RTT_max = max(self.RTT_max, message.time_alive)

        if self.competitive:
            self.competitive_receive(message)
        else:
            self.default_receive(message)

        # Bookkeeping for switching to competitive mode.
        d_q = self.RTT_st - self.RTT_min

        if d_q < 0.1 * (self.RTT_max - self.RTT_min):
            message.nearly_empty = True
        else:
            message.nearly_empty = False

    def default_receive(self, message):
        # Updating cwnd.
        d_q = self.RTT_st - self.RTT_min

        if d_q:
            lam_t = 1 / (self.delta * d_q)
            lam = self.cwnd / self.RTT_st

            if lam <= lam_t:
                self.cwnd += self.v / (self.delta * self.cwnd)
                if self.d == -1:
                    self.log_write("Minimum, cwnd = " + str(self.cwnd) + " time = " +
                                   str(self.time))
                    self.d = 1
            else:
                self.cwnd = max(self.cwnd - self.v / (self.delta * self.cwnd), 1)
                if self.d == 1:
                    self.log_write("Maximum, cwnd = " + str(self.cwnd) + " time = " +
                                   str(self.time))
                    self.d = -1

        else:
            self.cwnd += self.v / (self.delta * self.cwnd)
            if self.d == -1:
                self.log_write("Minimum, cwnd = " + str(self.cwnd) + " time = " +
                               str(self.time))
                self.d = 1

        # This whole block is for updating v.
        # This didn't really work with 3 rounds. Worked alright with 5 rounds.
        # With 3 it very consistently had a single jump to 2 and then back to 1.
        if message.ack_num >= self.last_in_window:
            if len(self.last_directions) == 4:
                self.last_directions.pop(0)

            if self.cwnd > self.prev_cwnd:
                direction = 1
            else:
                direction = -1
            self.last_directions.append(direction)

            total = sum(self.last_directions)

            if total == 4 or total == -4:
                self.v *= 2
                self.log_write("Doubled v, v=" + str(self.v) + ", in time " + str(self.time))
            else:
                self.v = 1

            self.prev_cwnd = self.cwnd
            self.last_in_window = self.ack_num + int(self.cwnd)

    def competitive_receive(self, message):
        if message.ack_num == self.expected_ack:
            self.expected_ack += 1
            self.cwnd += 1 / (self.delta * self.cwnd)
            self.dupack = 0
        elif message.ack_num > self.expected_ack:
            self.dupack += 1
            if self.dupack == 3:
                self.dupack = 0
                self.cwnd *= 0.5
                self.expected_ack = self.ack_num + 1

    def log_write(self, string):
        self.simulator.log_write("ID " + str(self.id) + ": " + string + "\n")
