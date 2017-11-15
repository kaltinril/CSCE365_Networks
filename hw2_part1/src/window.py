import message              # Python specific format to import custom module

#Globals
DEBUG = True  # Set to true for more printed information

class Window:

    def __init__(self):
        self.buffer = []
        self.buffer_size = 5

    def add_message(self, msg):
        found = False
        for s in self.buffer:
            if s.sequence_number == msg.sequence_number:
                found = True
                print("Debug: Found sequence, skipping add.") if DEBUG else None

        if self.is_room():
            print("Debug: No room in window!") if DEBUG else None
            if not found:
                self.buffer.append(msg)
                print("Debug: Appended message to window") if DEBUG else None
        # TODO: Add error message for more robust programming if no room

    # Receive a message and see if it was already ack'd
    # The message must be valid and the correct type
    def ack_message(self, msg):
        if msg:
            if msg.is_valid():
                print("Debug: valid") if DEBUG else None
                if msg.msg_type == "ack":
                    print("Debug: Ack") if DEBUG else None
                    self.__dequeue(msg.sequence_number)
            else:
                print("Debug: Invalid message!") if DEBUG else None

    def __dequeue(self, ackd_seq):
        i = len(self.buffer) - 1
        while i >= 0:
            msg = self.buffer[i]

            # Was this the packet that was ackd?
            if msg.sequence_number + len(msg.data) == ackd_seq:
                print("Debug: Deleting " + str(msg.sequence_number) + " " + msg.msg_type + " from Window") if DEBUG else None
                del self.buffer[i]

            i = i - 1

    def is_room(self):
        return len(self.buffer) <= self.buffer_size