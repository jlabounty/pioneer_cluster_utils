'''
    A utility for handling datasets and making files available between different nodes
'''
from dataclasses import dataclass
import queue 
import sys
import os
import subprocess
import zmq 
import time
import pickle
import uuid 

@dataclass
class DatasetMessage():
    filename : str  = ''    # Name of the file 
    recieved : bool = False # File was recieved by consumer, but has not yet been processed
    success  : bool = False # This file has been processed successfully
    request  : bool = False # This message is a request for a new file
    complete : bool = False # All files processed, consumer can exit
    consumer_id: str = None      # The unique ID of this consumer

    def encode(self):
        return pickle.dumps(self)
    
    @staticmethod
    def load(msg):
        return pickle.loads(msg)

class DatasetDistributer():

    @staticmethod
    def read_filelist(list):
        files = []
        with open(list, 'r') as f:
            for line in f:
                if(os.path.exists(line.strip())):
                    files.append(line.strip())
                else:
                    raise FileNotFoundError
        return files

    @staticmethod
    def from_args(*args,**kwargs):
        with open('tmp.txt', 'w') as f:
            for arc in args:
                f.write(arc)
        return DatasetDistributer('tmp.txt', **kwargs)

    def __init__(self, infile, port=5555, retry_until_all_complete=True, ntries=2, **kwargs):
        self.files = self.read_filelist(infile)
        self.port = port
        self.processed = {x:[False,False,False,0] for x in self.files} # Sent, Recieved, Confirmed Processed
        # self.generator = 
        self.retry = retry_until_all_complete
        self.nconnected = 0
        self.ntries = ntries
        self.consumers = []

    def run(self):
        print("Running the dataset distribution....")
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REP)
        self.socket.bind(f"tcp://*:{self.port}")
        # index = 0
        while True:
            msg = DatasetMessage.load( self.socket.recv() )
            print(f'Recieved message:', msg)
            if(msg.request):
                # requesting the next file

                if(msg.consumer_id not in self.consumers):
                    self.consumers.append(msg.consumer_id)

                found_file = False
                for file, vals in self.processed.items():
                    if(not vals[0] and not vals[1]):
                        self.socket.send(
                            DatasetMessage(filename=file, consumer_id=msg.consumer_id).encode()
                        )
                        self.processed[file][0] = True
                        self.processed[file][3] += 1
                        found_file = True 
                        break 
                if(not found_file):
                    # if(self.)
                    print("All files have been marked as sent!")
                    if(self.retry):
                        for file, vals in self.processed.items():
                            if(not vals[2] and vals[3] < self.ntries):
                                self.socket.send(
                                    DatasetMessage(filename=file,consumer_id=msg.consumer_id).encode()
                                )
                                # self.processed[file][0] = True
                                self.processed[file][3] += 1
                                found_file = True 
                                break
                if(not found_file): 
                    self.socket.send(
                        DatasetMessage(complete=True).encode()
                    )
                    self.consumers.remove(msg.consumer_id)
                continue 
            if(msg.complete):
                print("Message acknoledging completion recieved!")
            elif(msg.success):
                file = msg.filename
                print(f"File {file} was successfully processed!")
                self.processed[file][2]=True 
                # self.socket.send(msg.encode())
            elif(msg.recieved):
                # markign confirmation that the file was recieved
                file = msg.filename
                print(f"File {file} was successfully sent!")
                self.processed[file][1]=True 
                
            self.socket.send(msg.encode()) 
            print(self.processed)
            print(self.consumers)


class DatasetConsumer():
    def __init__(self, server='localhost', port=5555):
        self.context = zmq.Context()
        self.id = uuid.uuid4()
        print(f"This id: {self.id=}")

        #  Socket to talk to server
        print("Connecting to hello world server…")
        self.socket = self.context.socket(zmq.REQ)
        self.socket.connect(f"tcp://{server}:{port}")

    def send_message(self, msg):
        return self.socket.send(msg.encode())

    def recieve_message(self) -> DatasetMessage:
        return DatasetMessage.load(self.socket.recv())

    def get_next_file(self):
        print("Requesting next file")
        self.send_message(
            DatasetMessage(request=True, consumer_id=self.id)
        )
        message = self.recieve_message()
        print("Recieved message:", message)

        print("This file:", message.filename)
        message.recieved=True 

        # confirm receipt
        self.send_message(message)
        return self.recieve_message()
        return message.filename

    def confirm_processed(self, filename):
        if(type(filename) is str):
            self.send_message(
                DatasetMessage(filename,recieved=True, success=True)
            )
        elif(type(filename) is DatasetMessage):
            filename.success = True 
            self.send_message(filename)
        else:
            raise NotImplementedError
        return self.recieve_message()


        