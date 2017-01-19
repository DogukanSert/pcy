import sys
import timeit
import csv
import collections

basket_num = 0
filename = "prepared_dataset.csv"
support = 0
bucket_field = 1000
items_count = dict()
freq_items = list()
freq_pairs_count = dict()
pairs_hash_map = dict()
bitmap = list()

# Establish the value for the support threshold.
def set_init_vals():
    if (len(sys.argv) > 2):
        global support
        global basket_num
        support = int(sys.argv[1])
        basket_num = int(sys.argv[2])
        
    else:
        print "Please enter two arguments."
        sys.exit(0)
        
def hash_values(x, y):
    return (x*x + y*y) % bucket_field
    
def pass1():
    
    line_count = 0
    infile = open(filename, 'rb')
    inreader = csv.reader(infile)
    
    # Read items from the file, each line interpreted as a basket
    for basket in inreader:
        line_count += 1
        # Go through every item in every basket (line)
        for item in basket:
            # If the item is already in the directory,
            if item in items_count:
                # then increment it's count.
                items_count[item] = items_count[item] + 1
            else:
                # Otherwise, add it and set its count to 1
                items_count[item] = 1

        # Keep count for each bucket into which pairs are hashed
        for i in range(0, len(basket)):
            for j in range(i+1, len(basket)):
                pair = (basket[i], basket[j])
                hashed_val = hash_values(int(pair[0]), int(pair[1]))
                if hashed_val in pairs_hash_map:
                    pairs_hash_map[hashed_val] = pairs_hash_map[hashed_val] + 1
                else:
                    pairs_hash_map[hashed_val] = 1
        
        global basket_num
        if line_count == basket_num:
            break
        
    infile.close()
    
    # Filter dictionary so only frequent items are stored. At this point, counts no longer matter.
    global freq_items
    freq_items = (({item: count for item, count in items_count.items() if count >= support}).keys())
                
# Replace the buckets by a bit-vector
def between_passes():    
    position = 0
    # Initialize bitmap to zeros
    bitmap = [chr(0)]*bucket_field
    
    # Convert hash map to bitmap
    for pair in sorted(pairs_hash_map.keys()):
        if pairs_hash_map[pair] >= support:
            bitmap[position] = chr(ord((bitmap[position])) | 1)
        position = position + 1
            
    # Generate all possible pairs of frequent items
    for i in range(0, len(freq_items)):
        for j in range(i+1, len(freq_items)):
            if bitmap[hash_values(int(freq_items[i]), int(freq_items[j]))] > 0:
                if int(freq_items[i]) > int(freq_items[j]):
                    freq_pairs_count[(freq_items[j], freq_items[i])] = 0
                else:    
                    freq_pairs_count[(freq_items[i], freq_items[j])] = 0

# Only count pairs that hash to frequent buckets
def pass2():
    
    infile = open(filename)
    inreader = csv.reader(infile)
    
    for basket in inreader: 
        for pair in freq_pairs_count:
            # print "Checking if potential pairs are frequent"
            if(pair[0] in basket and pair[1] in basket):
                freq_pairs_count[pair] += 1
                
    infile.close()
       
start = timeit.default_timer()
set_init_vals()
pass1()
between_passes()
pass2()
end = timeit.default_timer()
runtime = end - start

freq_pairs_count = collections.OrderedDict(sorted(freq_pairs_count.items()))

print "Frequent pairs found:"
for pair in freq_pairs_count:
    if freq_pairs_count[pair] >= support:
        print pair, freq_pairs_count[pair]
print ""
print "Runtime of the program:", str(runtime), "seconds"
