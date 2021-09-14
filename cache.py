import math
import re
from optparse import OptionParser

parser = OptionParser()
parser.add_option('-a', '--associativity', default='2', action='store', type='string', dest='associativity')
parser.add_option('-c', '--cachesize', default='2048', action='store', type='string', dest='cachesize')
parser.add_option('-l', '--lines', default='10000', action='store', type='string', dest='lines')
parser.add_option('-f', '--file', default='gcc-10M.trace', action='store', type='string', dest='file')
(options, args) = parser.parse_args()
file = options.file
print('File: ', file)
cache_size_in_bits = int(options.cachesize)
in_associativity = [int(options.associativity)]
in_lines = [int(options.lines)]

#in_lines = [1000, 5000, 10000, 25000, 50000, 100000, 250000, 500000, 1000000, 2000000, 5000000, 10000000]
#in_associativity = [2, 4]

for lines in in_lines:
    for associativity in in_associativity:
        print("\n")
        print('Associativity: ', associativity)
        print('Cache size: ', cache_size_in_bits)
        count = 0
        populated = 0
        total_hit_count = 0
        total_miss_count = 0
        block_size = 1
        sets = cache_size_in_bits // block_size
        index_size = sets.bit_length() - 3

        references = cache_size_in_bits // (block_size * associativity)
        # create multidimensional arrays
        cache_lookup_table = [[-1] * associativity] * references
        history_table = [[-1] * associativity] * references

        # offset_bits corresponds to the bits used to determine the byte to be accessed from the cache line.
        # Ex: Because the cache lines are 4 bytes long, there are 2 offset bits.
        offset_bits = max(int(math.log(block_size) // math.log(2)), 1)

        try:
            with open(file) as fp:
                for cnt, line in enumerate(fp):
                    if lines == cnt:
                        break
                    # initialze loop variables
                    count = cnt
                    missed = True
                    # greedy space split each line
                    addr = re.split('\s+', line)[9]
                    # Memory Address indicates the address accessed by a load or store.
                    # If the micro-op doesn't access memory, this field will have the value zero.
                    # [64-bit hexadecimal]
                    if addr == '0':
                        continue
                    # Tag corresponds to the remaining bits. This means there are 14 – (6+2) = 6 tag bits,
                    # which are stored in tag field to match the address on cache request.
                    tag = int('0x' + addr, 16) >> index_size - offset_bits
                    # convert from hex and get relevant address bits
                    index = int(str(bin(int('0x' + addr, 16)))[-offset_bits - index_size:-offset_bits], 2)

                    # check for hit
                    for i in range(associativity):
                        # hit!
                        if cache_lookup_table[index][i] == tag:
                            # record cache hit and time
                            history_table[index][i] = count
                            missed = False
                            total_hit_count += 1
                            break
                    # cache replace/populate
                    for i in range(associativity):
                        if missed and cache_lookup_table[index][i] == -1:
                            cache_lookup_table[index][i] = tag
                            history_table[index][i] = count
                            total_miss_count += 1
                            missed = True
                            break
                    if missed:
                        record_oldest = 0
                        oldest = history_table[index][0]
                        for k in range(associativity):
                            if history_table[index][k] < oldest:
                                record_oldest = k
                                oldest = history_table[index][k]
                        cache_lookup_table[index][record_oldest] = tag
                        history_table[index][record_oldest] = count
                        total_miss_count += 1

        except Exception:
            raise FileNotFoundError("Failed to process trace file gcc-1k.trace")
        # account for starting at 0
        count += 1

        print('Total traces: ', count)
        print("Cache requests: ", total_hit_count + total_miss_count)
        print("Cache hits: ", total_hit_count)
        print("Cache misses: ", total_miss_count)
        print("Hit rate: ", format((total_hit_count) / (total_hit_count + total_miss_count), '.4f'))
        print("Miss rate: ", format((total_miss_count) / (total_hit_count + total_miss_count), '.4f'))
