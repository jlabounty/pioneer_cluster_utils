import os
import time
import platform

def form_outfile(infile):
    outfile = infile.split("/")[-1]
    if('/run' in infile):
        run = infile.split("/run")[1].split("/")[0]
        outfile = outfile.replace(".", f'_run_{run}.')
    if('/subrun' in infile):
        subrun = infile.split("/subrun")[1].split("/")[0]
        outfile = outfile.replace(".", f'_subrun_{subrun}.')
    return outfile.replace("root", 'pickle')

def check_queue(lim=5, queue_dir='/queue/'):
    return len(os.listdir(queue_dir)) < lim

def copy_file(infile,indir, rsync_options=''):
    assert os.path.exists(infile)
    assert os.path.exists(indir)
    os.system(f'rsync -a {rsync_options} {infile} {indir}')
    return os.path.join(indir, infile.split("/")[-1])

def create_queue_file(queue_dir):
    file = os.path.join(queue_dir, f'queue_file_{time.time()}')
    os.system(f'touch {file}')
    return file

def remove_queue_file(queue_file):
    # print("removing queue file", queue_file)
    os.system(f'rm -f {queue_file}')

def copy_file_with_queue(infile, indir='./', sleep=10, max_tries = 100, queue_dir='/queue/'):
    print("Entering copy queue!")
    print('   -> Looking at:', queue_dir)
    counter = 0
    while True:
        if(check_queue(queue_dir=queue_dir)):
            queue_file = create_queue_file(queue_dir)
            file =  copy_file(infile, indir)
            remove_queue_file(queue_file)
            return file
        else:
            print(f'   -> Queue is full, waiting ({counter})...')
            counter += 1
            if(counter >= max_tries):
                raise TimeoutError
            time.sleep(sleep)

class FileHandler:
    def __init__(self, infile, single_file=True, automatic_rules=True, queue_dir = '/queue/', delete_local_copies=True, **kwargs):
        print('Initializing!!!', queue_dir)
        self.infile = infile 
        self.single_file = single_file
        if(not single_file):
            self.file_list = self.read_file_list(infile)
        else:
            self.file_list = [infile]

        print('Files handled by this handler:', self.file_list)
        self.host = self._identify_host()
        if(automatic_rules):
            self._set_host_rules()
        self.queue_dir = queue_dir
        if(not os.path.exists(self.infile)):
            print("Warning: this file does not exist ->", infile)
        self.delete_local_copies = delete_local_copies
        self.localpath = None 

    def read_file_list(self,infile):
        files = []
        with open(infile, 'r') as f:
            for line in f:
                files.append(line.strip())
        return files

    def _identify_host(self):
        '''identify the host this is running on'''
        # https://stackoverflow.com/questions/4271740/how-can-i-use-python-to-get-the-system-hostname#comment73605463_4271873
        return os.getenv('HOSTNAME', os.getenv('COMPUTERNAME', platform.node())).split('.')[0]

    def _set_host_rules(self):
        '''set rules for copying files in place and number of retries automatically based on hostname'''
        print(f"Setting rules based on {self.host=}")
        if('cenpa-rocks' in self.host):
            self.set_copy_rules(False, -1,-1)
        elif('compute-' in self.host):
            self.set_copy_rules(True, 100, 30)
        else:
            self.set_copy_rules(False, -1,-1)

    def set_copy_rules(self, copy_files=True, ntries=100, wait_time=10):
        self.copy_files = copy_files
        self.ntries = ntries 
        self.wait_time = wait_time

    def __enter__(self):
        return self 

    def __exit__(self,exception_type, exception_value, traceback):
        if(self.delete_local_copies):
            self.remove_local_copy()
        if(exception_type is not None):
            print('Warning: exception raised:', exception_type, exception_value)
            print(traceback)
    
    def remove_local_copy(self):
        if(self.localpath is not None and os.path.exists(self.localpath)):
            os.system(f'rm -f {self.localpath}')

    def __iter__(self):
        print(self.queue_dir)
        for file in self.file_list:
            self.raw_file_path = file 
            if(self.copy_files):
                if(self.localpath is not None):
                    self.remove_local_copy()
                    self.localpath = None                 
                self.localpath = copy_file_with_queue(file, sleep=self.wait_time, max_tries=self.ntries, queue_dir=self.queue_dir)
                yield self.localpath
            else:
                yield file

