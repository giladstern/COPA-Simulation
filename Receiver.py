from random import shuffle

class Receiver:
    def __init__(self, simulator, buff_size, serve_per_timestep):
        self.simulator = simulator
        self.buff_size = buff_size
        self.serve_per_timestep = serve_per_timestep
        self.buffer = []
        self.current_messages = []

    def receive(self, message):
        self.current_messages.append(message)

    def timestep(self):
        shuffle(self.current_messages)

        for message in self.current_messages:
            if len(self.buffer) < self.buff_size:
                self.buffer.append(message)
            else:
                self.simulator.log_write("Message #" + str(message.ack_num) + " dropped!\n")

        self.current_messages.clear()

        num_messages = min(self.serve_per_timestep, len(self.buffer))
        for i in range(num_messages):
            message = self.buffer.pop(0)
            message.in_buffer = False
            self.simulator.send_message(message)

        # TODO: Check if need to flip.
        for message in self.buffer:
            message.timestep()
