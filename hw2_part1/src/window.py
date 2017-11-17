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
                print("Debug: Found sequence, skipping add. " + str(msg.sequence_number)) if DEBUG else None

        if self.is_room():
            if not found:
                self.buffer.append(msg)
                print("Debug: Appended message to window " + str(msg.sequence_number)) if DEBUG else None
        else:
            print("Debug: No room in window!") if DEBUG else None
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
        ackd_something = False
        while i >= 0:
            msg = self.buffer[i]

            print("DEBUG: Attempt Dequeue on " + str(msg.sequence_number) + " with len " + str(len(msg.data))) if DEBUG else None

            # Was this the packet that was ackd?
            if msg.sequence_number + len(msg.data) == ackd_seq:
                print("Debug: Deleting " + str(msg.sequence_number) + " " + msg.msg_type + " from Window") if DEBUG else None
                del self.buffer[i]
                ackd_something = True

            i = i - 1

        if DEBUG and not ackd_something:
            print("DEBUG: Didn't find any matching packets " + str(ackd_seq))

    def is_room(self):
        # print("DEBUG: Window Buffer size: " + str(len(self.buffer))) if DEBUG else None
        return len(self.buffer) < self.buffer_size

    def is_empty(self):
        return len(self.buffer) == 0
