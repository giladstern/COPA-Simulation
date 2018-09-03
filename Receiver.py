from random import shuffle, choice

class Receiver:
    def __init__(self, simulator, buff_size, serve_per_timestep):
        self.simulator = simulator
        self.buff_size = buff_size
        self.serve_per_timestep = serve_per_timestep
        self.buffer = []
        self.current_messages = dict()

    def receive(self, message):
        # self.current_messages.append(message)
        if message.dest not in self.current_messages:
            self.current_messages[message.dest] = [message]
        else:
            self.current_messages[message.dest].append(message)

    def timestep(self):
        keys = list(self.current_messages.keys())
        while keys and len(self.buffer) < self.buff_size:
            key = choice(keys)
            self.buffer.append(self.current_messages[key].pop(0))
            if not self.current_messages[key]:
                keys.remove(key)
        self.current_messages.clear()
        # shuffle(self.current_messages)
        #
        # for message in self.current_messages:
        #     if len(self.buffer) < self.buff_size:
        #         self.buffer.append(message)
        #     else:
        #         self.simulator.log_write("Message #" + str(message.ack_num) + " dropped!\n")

        self.current_messages.clear()

        num_messages = min(self.serve_per_timestep, len(self.buffer))
        for i in range(num_messages):
            message = self.buffer.pop(0)
            message.in_buffer = False
            self.simulator.send_message(message)

        # TODO: Check if need to flip.
        for message in self.buffer:
            message.timestep()
