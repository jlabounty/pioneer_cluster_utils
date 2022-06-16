import os
# import sys
# import pickle
import time
# import uproot

def form_outfile(infile):
    outfile = infile.split("/")[-1]
    if('/run' in infile):
        run = infile.split("/run")[1].split("/")[0]
        outfile = outfile.replace(".", f'_run_{run}.')
    if('/subrun' in infile):
        subrun = infile.split("/subrun")[1].split("/")[0]
        outfile = outfile.replace(".", f'_subrun_{subrun}.')
    return outfile.replace("root", 'pickle')

def check_queue(lim=5):
    return len(os.listdir('/queue/')) < lim

def copy_file(infile,indir):
    os.system(f'rsync -a {infile} {indir}')
    return os.path.join(indir, infile.split("/")[-1])

def copy_file_with_queue(infile, indir='./', sleep=10, max_tries = 100):
    print("Entering copy queue!")
    counter = 0
    while True:
        if(check_queue()):
            return copy_file(infile, indir)
        else:
            print(f'   -> Queue is full, waiting ({counter})...')
            counter += 1
            if(counter >= max_tries):
                raise TimeoutError
            time.sleep(sleep)