from pioneer_cluster_utils.data_handler import *

infile = './files.txt'
data_dir = './data/'
files = [os.path.join(data_dir, f'file_{i}.txt') for i in range(10)]
os.system(f'mkdir -p {data_dir}')
with open(infile, 'w') as f:
    for file in files:
        f.write(file+'\n')
        os.system(f'touch {file}')

# ding = DatasetDistributer(infile)
ding = DatasetDistributer(infile, timeout=1.)
print(ding, ding.files)

ding.run()

for i,x in enumerate(files):
    assert os.path.exists(x)
    assert os.path.exists(x.replace('.txt', f'_processed_{i%3}.txt'))


print("Tests passed. Cleaning up.")
os.system(f'rm -rf {data_dir}')
os.system(f'rm -rf {infile}')