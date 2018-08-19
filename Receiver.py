class Receiver:
    def __init__(self, simulator, buff_size, serve_per_timestep):
        self.simulator = simulator
        self.buff_size = buff_size
        self.serve_per_timestep = serve_per_timestep
        self.buffer = []

    def receive(self, message):
        if len(self.buffer) < self.buff_size:
            self.buffer.append(message)

    def timestep(self):
        num_messages = min(self.serve_per_timestep, len(self.buffer))
        for i in range(num_messages):
            message = self.buffer.pop(0)
            message.in_buffer = False
            self.simulator.send_message(message)

        for message in self.buffer:
            message.timestep()
