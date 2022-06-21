from pioneer_cluster_utils.data_handler import *

dongs = [DatasetConsumer(id=i) for i in range(3)]
# dong = DatasetConsumer(server='cenpa-rocks') #rocks testing, only change needed!

for request in range(15):
    for dong in dongs:
        print("Sending request %s …" % request)
        this_file = dong.get_next_file()

        if(this_file.complete):
            print("All files have been successfully processed! Exiting!")
            # dong.confirm_processed(this_file)
            break 

        time.sleep(1)

        if(request != 6):

            outfile = this_file.filename.replace(".txt", f'_processed_{this_file.consumer_id}.txt')
            os.system(f'touch {outfile}')

            msg = dong.confirm_processed(this_file)
            print(msg)



            # self.socket.send(
            #     DatasetMessage(filename=message.filename, success=True).encode()
            # )
            # self.socket.recv()

            time.sleep(1)

for dong in dongs:
    dong.get_next_file()

print("All done!")