from pioneer_cluster_utils.queue import FileHandler
import os
import time

# create files
file_list = './file_list.txt'
queue_dir = './queue/'
test_dir = './data/'
test_files = [os.path.join(test_dir, f'file_{i}.txt') for i in range(3)]

os.system(f'mkdir -p {test_dir}')
os.system(f'mkdir -p {queue_dir}')
with open(file_list, 'w') as f:
    for x in test_files:
        f.write(f'{x}\n')
        os.system(f"touch {x}")

# test the file handler with queue
with FileHandler(file_list, single_file=False, queue_dir=queue_dir) as fh:
    # fh.queue_dir = queue_dir
    print(fh.queue_dir)
    assert len(fh.file_list) == len(test_files)
    assert set(fh.file_list) == set(test_files)
    fh.set_copy_rules(True, 100, 10)
    print(fh, fh.queue_dir)
    for x in fh:
        print(x)
        assert os.path.exists(x)
        print(os.listdir(queue_dir))
        time.sleep(1)

# test the file handler without queue
with FileHandler(file_list, single_file=True, queue_dir=queue_dir) as fh:
    # fh.queue_dir = queue_dir
    print(fh.queue_dir)
    assert len(fh.file_list) == 1
    # assert set(fh.file_list) == set(test_files)
    fh.set_copy_rules(False, -1, -1)
    print(fh, fh.queue_dir)
    for x in fh:
        print(x)
        assert os.path.exists(x)
        assert x == file_list
        time.sleep(1)


# clean up
os.system(f'rm -fr {test_dir}')
os.system(f'rm -fr {queue_dir}')
os.system(f'rm -fr {file_list}')