import binascii             # Using this as a way to create a checksum


class Message:
    types = {"Start", "data", "ack", "end"}  # Allowed Message Types
    max_data = 1460

    def __init__(self, msg_type, sequence_number, data):
        self._msg_type = msg_type
        self._sequence_number = sequence_number
        self._data = data
        self.__restrict_data()  # Make sure that if this is an ACK, we clear the data
        self.checksum = self.__generate_checksum()

    # Public Mutator/Accessor properties
    @property
    def msg_type(self):
        return self._msg_type

    @msg_type.setter
    def msg_type(self, value):
        # Make sure that we were provided a valid message type.
        if value in Message.types:
            self._msg_type = value
        else:
            raise ValueError("Message Type must be one of the following: "
                             + ", ".join(Message.types))

    @property
    def sequence_number(self):
        return self._sequence_number

    @sequence_number.setter
    def sequence_number(self, value):
        if value.isumeric():
            self._sequence_number = value
        else:
            raise ValueError("Sequence Number supplied must be a positive number")

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, value):
        # Data can not be more than the max
        if len(value) > Message.max_data:
            raise ValueError("Maximum data length" + str(Message.max_data) + " exceeded: " + str(value))
        else:
            self._data = value

    # Static Methods to be used if we don't have a reference to this
    @staticmethod
    def generate_checksum(data):
        return binascii.crc32(data)

    @staticmethod
    def validate_checksum(data, checksum):
        return checksum == Message.generate_checksum(data)

    # Private methods

    def __restrict_data(self):
        # Per the documentation ack can not send data, set it to ""
        if self.msg_type == "ack":
            self.data = ""

    # __combine_data:
    # Combines the message type, sequence number, and data in a consistent way
    def __combine_data(self):
        return self.msg_type + self.sequence_number + self.data

    # __generate_checksum
    # Simple helper method to pass instance variable data into static method
    def __generate_checksum(self):
        data = self.__combine_data()
        return self.generate_checksum(data)

    # __validate_checksum
    # Simple helper method to pass instance variable data into static method
    def __validate_checksum(self):
        data = self.__combine_data()
        return Message.validate_checksum(data, self.checksum)
