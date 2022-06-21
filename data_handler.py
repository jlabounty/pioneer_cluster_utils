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

@dataclass
class DatasetMessage():
    filename : str  = ''
    recieved : bool = False 
    consumed : bool = False 
    success  : bool = False
    request  : bool = False

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

    def __init__(self, infile, port=5555, **kwargs):
        self.files = self.read_filelist(infile)
        self.port = port
        self.processed = {x:[False,False,False] for x in self.files} # Sent, Recieved, Confirmed Processed
        # self.generator = 

    def run(self):
        print("Running the dataset distribution....")
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REP)
        self.socket.bind(f"tcp://*:{self.port}")
        index = 0
        while True:
            msg = DatasetMessage.load( self.socket.recv() )
            print(f'Recieved message:', msg)
            if(msg.request):
                # requesting the next file
                self.socket.send(
                    DatasetMessage(filename=self.files[index]).encode()
                )
                self.processed[self.files[index]][0] = True
                index += 1
                continue 
            
            if(msg.success):
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


class DatasetConsumer():
    def __init__(self, server='localhost', port=5555):
        self.context = zmq.Context()

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
            DatasetMessage(request=True)
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


        