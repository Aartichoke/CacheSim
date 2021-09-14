Usage:
gcc-1K.trace or a specified file must be in same directory, uncompressed
Enter total cache size in bits, and the associativity
prompt> ./paging-policy.py  --cachesize=2048 --associativity=4 --lines=500000 --file=gcc.10M.trace

And what you would see is:
Associativity:  4
Cache size:  2048
Lines:  500000
File:  gcc-10M.trace
Total traces:  10000000
Cache requests:  3140158
Cache hits:  2440510
Cache misses:  699648
Hit rate:  0.7772
Miss rate:  0.2228