class Message:
    def __init__(self, source, dest, ack_num):
        self.source = source
        self.dest = dest
        self.ack_num = ack_num
        self.ttl = 0
        self.time_alive = 0
        self.in_buffer = False
        self.received = -1

    def timestep(self):
        self.time_alive += 1

        if not self.in_buffer:
            self.ttl -= 1

            if self.ttl <= 0:
                self.dest.receive(self)

    def enqueue(self):
        self.in_buffer = True
        self.dest, self.source = self.source, self.dest
