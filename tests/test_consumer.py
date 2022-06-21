from pioneer_cluster_utils.data_handler import *

dong = DatasetConsumer()
# dong = DatasetConsumer(server='cenpa-rocks') #rocks testing, only change needed!

for request in range(10):
        print("Sending request %s …" % request)
        this_file = dong.get_next_file()

        time.sleep(1)

        msg = dong.confirm_processed(this_file)
        print(msg)

        # self.socket.send(
        #     DatasetMessage(filename=message.filename, success=True).encode()
        # )
        # self.socket.recv()

        time.sleep(1)