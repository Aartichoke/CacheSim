#! /usr/bin/env python

import sys
from optparse import OptionParser
import random
import math

def convert(size):
    length = len(size)
    lastchar = size[length-1]
    if (lastchar == 'k') or (lastchar == 'K'):
        m = 1024
        nsize = int(size[0:length-1]) * m
    elif (lastchar == 'm') or (lastchar == 'M'):
        m = 1024*1024
        nsize = int(size[0:length-1]) * m
    elif (lastchar == 'g') or (lastchar == 'G'):
        m = 1024*1024*1024
        nsize = int(size[0:length-1]) * m
    else:
        nsize = int(size)
    return nsize

def hfunc(index):
    if index == -1:
        return 'MISS'
    else:
        return 'HIT '

def vfunc(victim):
    if victim == -1:
        return '-'
    else:
        return str(victim)

#
# main program
#
parser = OptionParser()
parser.add_option('-f', '--addressfile', default='gcc-1K.trace',   help='a file with a bunch of addresses in it',                                action='store', type='string', dest='addressfile')
parser.add_option('-n', '--numaddrs', default='10',    help='if -a (--addresses) is -1, this is the number of addrs to generate',    action='store', type='string', dest='numaddrs')
parser.add_option('-p', '--policy', default='FIFO',    help='replacement policy: FIFO, LRU, OPT, UNOPT, RAND, CLOCK',                action='store', type='string', dest='policy')
parser.add_option('-C', '--cachesize', default='4',    help='size of the page cache, in pages',                                      action='store', type='string', dest='cachesize')
parser.add_option('-N', '--notrace', default=False,    help='do not print(out a detailed trace',                                     action='store_true', dest='notrace')
parser.add_option('-c', '--compute', default=False,    help='compute answers for me',                                                action='store_true', dest='solve')

(options, args) = parser.parse_args()

print('ARG addressfile', options.addressfile)
print('ARG numaddrs', options.numaddrs)
print('ARG policy', options.policy)
print('ARG cachesize', options.cachesize)
print('ARG notrace', options.notrace)
print('')

addressFile = str(options.addressfile)
numaddrs    = int(options.numaddrs)
cachesize   = int(options.cachesize)
policy      = str(options.policy)
notrace     = options.notrace

# seed random for simulation consistency
random.seed(0)

addrList = []
if addressFile != '':
    fd = open(addressFile)
    for line in fd:
        addrList.append(int(line))
    fd.close()
print(addrList)
exit()

if options.solve == False:
    print('Assuming a replacement policy of %s, and a cache of size %d pages,' % (policy, cachesize))
    print('figure out whether each of the following page references hit or miss')
    print('in the page cache.\n')

    for n in addrList:
        print('Access: %d  Hit/Miss?  State of Memory?' % int(n))
    print('')

else:
    if notrace == False:
        print('Solving...\n')

    # init memory structure
    count = 0
    memory = []
    hits = 0
    miss = 0

    if policy == 'FIFO':
        leftStr = 'FirstIn'
        riteStr = 'Lastin '
    elif policy == 'LRU':
        leftStr = 'LRU'
        riteStr = 'MRU'
    elif policy == 'MRU':
        leftStr = 'LRU'
        riteStr = 'MRU'
    elif policy == 'RAND':
        leftStr = 'Left '
        riteStr = 'Right'
    else:
        print('Policy %s is not yet implemented' % policy)
        exit(1)

    # track reference bits for clock
    ref = {}

    cdebug = False

    # need to generate addresses
    addrIndex = 0
    for nStr in addrList:
        # first, lookup
        n = int(nStr)
        try:
            idx = memory.index(n)
            hits = hits + 1
            if policy == 'LRU' or policy == 'MRU':
                update = memory.remove(n)
                memory.append(n) # puts it on MRU side
        except:
            idx = -1
            miss = miss + 1

        victim = -1        
        if idx == -1:
            # miss, replace?
            # print('BUG count, cachesize:', count, cachesize
            if count == cachesize:
                # must replace
                if policy == 'FIFO' or policy == 'LRU':
                    victim = memory.pop(0)
                elif policy == 'MRU':
                    victim = memory.pop(count-1)
                elif policy == 'RAND':
                    victim = memory.pop(int(random.random() * count))
            else:
                # miss, but no replacement needed (cache not full)
                victim = -1
                count = count + 1

            # now add to memory
            memory.append(n)
            if cdebug:
                print('LEN (a)', len(memory))
            if victim != -1:
                assert(victim not in memory)

        # after miss processing, update reference bit
        if n not in ref:
            ref[n] = 1
        else:
            ref[n] += 1
        
        if cdebug:
            print('REF (a)', ref)

        if notrace == False:
            print('Access: %d  %s %s -> %12s <- %s Replaced:%s [Hits:%d Misses:%d]' %
                  (n, hfunc(idx), leftStr, memory, riteStr, vfunc(victim), hits, miss))
        addrIndex = addrIndex + 1
        
    print('')
    print('FINALSTATS hits %d   misses %d   hitrate %.2f'
          % (hits, miss, (100.0*float(hits))/(float(hits)+float(miss))))
    print('')



    
    
    







