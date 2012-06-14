from __future__ import generators
import whrandom, general_functions,random


def pair_list(count):
    result =[]
    for i in range(0, count):
        for j in range(i+1, count):
            result.append([i,j])
    return result

def first_sort(a, b):
    return cmp(a[0], b[0])

def shuffle(list):
    pairs = []
    for element in list:
        pairs.append([whrandom.random(), element])
    pairs.sort(first_sort)
    result = map(lambda x: x[1], pairs)
    return result

def randsort(a,b):
	return  (random.randint(0,1)*2)-1

def shuff(list):
	list.sort(randsort)
	return list
    
def swap(list,(source_index, destination_index)):
	source = list[source_index]
	destination = list[destination_index]
	#re-assigns members
	list[source_index] = destination
	list[destination_index] = source
	
	return list

def check_index(member, list):
	i=0
	for e in list:
		if e == member:
			return i
			break
		i+=1
	return None
	
def perm(arr,N=None):
  if N is None: N=len(arr)-1
  if N>1:
    for i in perm(arr,N-1): yield i
  else: yield arr
  for k in range(N):
    if N&1: (arr[N] , arr[k]) = (arr[k], arr[N])
    else:   (arr[N] , arr[0]) = (arr[0], arr[N])
    if N>1:
      for i in perm(arr,N-1): yield i
    else: yield arr

def continuity_check(list):
	ticker = 0
	i = 1
	while i < len(list):
		ahead = list[i]
		behind = list[i-1]
		comparison = 0
		j = 0
		while j < len(ahead):
			if ahead[j] == behind[j]:
				comparison+=1
			j+=1
		if comparison == len(ahead)-2:
			print 'entry %d is ok' % i
		else:
			ticker+=1
			print 'entry %d is fucked ass up!' % i, ticker
			print comparison
		i+=1
		

def all_perms(element_list):
	allperms=[list(i) for i in perm(element_list)]
	return allperms
def shuff_perms(element_list):
	element_list.sort(general_functions.randsort)
	return all_perms(element_list)

def unique_perms(list):
	unique_perms = []
	total_perms = all_perms(list)
	for perm in total_perms:
		if perm not in unique_perms:
			unique_perms.append(perm)
	return unique_perms
	
def random_perms(element_list):
	total_perms = all_perms(element_list)
	current_group = element_list
	used_list = []
	available_swaps = pair_list(len(element_list))
	#used_list.append(element_list)
	ticker = 0
	i = 0
	while len(used_list) < general_functions.factorial(len(element_list)):# i < len(total_perms)/len(available_swaps):
		available_swaps.sort(general_functions.randsort)
		j=0
		while j < len(available_swaps):
			pair = available_swaps[j]
			trying = swap(current_group,pair)
			if trying not in used_list:
				current_group = trying#swap(current_group,pair)
				append_group = trying+[]
				
				used_list.append(append_group+[])#.append(append_group)
				#print used_list
			elif j == len(available_swaps)-1:
				print 'fucking shit, cant find an unused swappable pair!!!!!!!!!'
				ticker+=1
			j+=1
		i+=1
	print '%d fuckups'%ticker
	return used_list


def transpose(list):
	list_size = len(list)
	list_index =0
	pairs = pair_list(list_size)
	shuffled_pairs = shuffle(pairs)
	def swap_perm(list, index):
		
		#print swap_one.list_index,'List index'
		index = index%(len(shuffled_pairs))
		swapped_list = swap(list,(shuffled_pairs[index]))
		#self.list_index +=1
		#self.list_index = self.list_index%(len(self.shuffled_pairs))
		return swapped_list
	def fill_list(list):
		total = []
		i = 0
		while i < general_functions.factorial(len(list)):
			b = (swap_perm(list, i))+[]
			total.append(b)
			i+=1
		return total
	return fill_list(list)
	
	
class swap_one:
	
	
	def __init__(self,list = [1,2,3]):
		self.list_size = len(list)
		if self.list_size < 2:
			raise ValueError("list must be of 2 or more members")
		swap_one.list_index =0
		self.pairs = pair_list(self.list_size)
		self.shuffled_pairs = shuffle(self.pairs)
	
	def swap_perm(self,list, index):
		
		#print swap_one.list_index,'List index'
		index = index%(len(self.shuffled_pairs))
		swapped_list = swap(list,(self.shuffled_pairs[index]))
		self.list_index +=1
		self.list_index = self.list_index%(len(self.shuffled_pairs))
		return swapped_list
	def fill_list(self, list):
		total = []
		i = 0
		while i < general_functions.factorial(len(list)):
			b = (self.swap_perm(list, i))+[]#WHY THE HELL DO I HAVE TO DO THIS????
			#print b
			total.append(b)
			i+=1
		return total
s=swap_one([1,2,3])

def permute_list(list):
	if len(list) > 1:
		return s.swap_perm(list)
	else:
		return list