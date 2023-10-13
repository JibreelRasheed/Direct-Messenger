import socket, json, time


class RetrievalError(Exception):
    """This exception is to be raised whenever an error occurs while trying to retrieve messages from the server."""
    pass


class ConnectError(Exception):
    """This exception is to be raised whenever an error occurs while trying to connect to the server."""
    pass


class DirectMessage:
    """Used to store attributes of messages sent to a user, separated by sender/recipient attribute."""

    def __init__(self):
        recipient = None
        message = None
        timestamp = None


class DirectMessenger:
    """An object containing all the attributes required to send a message to a recipient."""

    def __init__(self, dsuserver='168.235.86.101', username=None, password=None, port=3021):
        self.dsuserver = dsuserver
        self.username = username
        self.password = password
        self.port = port
        self.token = None

    def _connect(self):
        """Connects to a server and populates the token attribute."""
        # No "with" used when connecting as that would close the connection at the end of the function, function exists to establish a connection that is to be closed by external code
        try:
            self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client.connect((self.dsuserver, self.port))
            self.sender = self.client.makefile('w')
            self.recv = self.client.makefile('r')

            join_msg = {"join": {"username": self.username, "password": self.password, "token": ""}}
            loaded_message = json.dumps(join_msg)

            self.sender.write(loaded_message + '\r\n')
            self.sender.flush()

            srv_message = self.recv.readline()
            diction = json.loads(srv_message)
            if diction["response"]["type"] != "ok":
                # If the server returns a message besides ok, then an error must have occurred.
                raise ConnectError(diction["response"]["message"])
            else:
                # Populating token attribute so that it may be called outside of this function
                self.token = diction["response"]["token"]
        except Exception as exc:
            # Raises an error if
            raise ConnectError(exc)
        return

    def send(self, message: str = None, recipient: str = None) -> bool:
        """Attempts to send a message to a recipient, returns true if message successfully sent, false if send failed."""
        try:
            self._connect()
            timestamp = time.time()
            poster = {"token": self.token,
                      "directmessage": {"entry": message, "recipient": recipient, "timestamp": timestamp}}
            get_dumped = json.dumps(poster)
            self.sender.write(get_dumped + '\r\n')
            self.sender.flush()
            # Reads server's response message to determine if message successfully sent
            if 'ok' in str(self.recv.readline()):
                self.client.close()
                return True
            else:
                self.client.close()
                return False
        except ConnectError as exc:
            raise exc
        except Exception as exc:
            raise exc

    def retrieve_new(self) -> list:
        """Returns a list of DirectMessage objects containing all new messages."""
        try:
            self._connect()
        except ConnectError as exc:
            raise exc
        else:
            try:
                poster = {"token": self.token, "directmessage": "new"}
                get_dumped = json.dumps(poster)
                self.sender.write(get_dumped + '\r\n')
                self.sender.flush()
                full_response = self.recv.readline()
                # Converts server response to a dict -> Allows it to be indexed by string
                full_response = json.loads(full_response)
                if full_response["response"]["type"] != "ok":
                    raise RetrievalError(full_response["response"]["message"])
                else:
                    # Appends only unique recipients to a list
                    list_garbo = []
                    for obj in full_response['response']['messages']:
                        if obj['from'] not in list_garbo:
                            list_garbo.append(obj['from'])

                    # Creates a directmessage object for each user in list_garbo containing all their messages and respective timestamps
                    temp_list = []
                    for user in list_garbo:
                        temp_direct = DirectMessage()
                        temp_direct.recipient = user
                        temp_direct.message = []
                        temp_direct.timestamp = []
                        for each_message in (full_response['response']['messages']):
                            # Ensures messages are appended to the correct user's message list
                            if user == each_message['from']:
                                temp_direct.message.append(each_message['message'])
                                temp_direct.timestamp.append(each_message['timestamp'])
                        temp_list.append(temp_direct)

                    self.client.close()
                    return (temp_list)
            except Exception as exc:
                raise RetrievalError(exc)

    def retrieve_all(self) -> list:
        """Returns a list of DirectMessage objects containing all messages."""
        try:
            self._connect()
        except ConnectError as exc:
            raise exc
            return []
        else:
            try:
                poster = {"token": self.token, "directmessage": "all"}
                get_dumped = json.dumps(poster)
                self.sender.write(get_dumped + '\r\n')
                self.sender.flush()
                full_response = self.recv.readline()
                # Converts server response to a dict -> Allows it to be indexed by string
                full_response = json.loads(full_response)
                if full_response["response"]["type"] != "ok":
                    raise RetrievalError(full_response["response"]["message"])
                else:
                    # Appends only unique recipients to a list
                    list_garbo = []
                    for obj in full_response['response']['messages']:
                        if obj['from'] not in list_garbo:
                            list_garbo.append(obj['from'])

                    # Creates a directmessage object for each user in list_garbo containing all their messages and respective timestamps
                    temp_list = []
                    for user in list_garbo:
                        temp_direct = DirectMessage()
                        temp_direct.recipient = user
                        temp_direct.message = []
                        temp_direct.timestamp = []
                        for each_message in (full_response['response']['messages']):
                            # Ensures messages are appended to the correct user's message list
                            if user == each_message['from']:
                                temp_direct.message.append(each_message['message'])
                                temp_direct.timestamp.append(each_message['timestamp'])
                        temp_list.append(temp_direct)

                    self.client.close()
                    return (temp_list)
            except Exception as exc:
                raise RetrievalError("There was an error retrieving direct messages: " + exc)
