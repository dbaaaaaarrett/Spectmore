#!usr/bin/python
import random, string, math, os
from random import Random

def repeat_element(element, times):
	list = []
	i=0
	while i < times:
		list.append(element)
		i+=1
	return list

def check_index(member, list):
	i=0
	for e in list:
		if e == member:
			return i
			break
		i+=1
	return None

def twice_each_element(list, how_many = 2):
	new_list = []
	for e in list:
		i = 0
		while i < how_many:
			new_list.append(e)
			i+=1
	return new_list

def quantize(float, quantize):
	close = 0
	i = 0
	while close < float:
		close = i*quantize
		i+=1
	#float = quantize + close
	return close

def if_none(test_value, result_value):
    if test_value == None:
        return result_value
    else:
        return test_value

def write_data_as_function(data, (function_name,file_name)):
	function = 'def '+function_name+'():\n	return'+str(data)+'\n'
	if os.path.exists(file_name+'.py') == 1:
		write = 'a'
	elif os.path.exists(file_name+'.py') == 0:
		write = 'w'
	page = open(file_name+'.py',write)
	page.write(function)


def combine_dicts(dict_list):# Combining dictionaries - each one overrides (shadows) previous:
    result = {}  # It's a dict, too.
    for dict in dict_list:
        for key in dict.keys():
            result[key] = dict[key]
    return result

def random_swap(list):
	first_random_list_index = random.randint(0,len(list)-1)
	second_random_list_index = random.randint(0,len(list)-1)
	if len(list) > 1:#checks more than 1 list element
		while first_random_list_index == second_random_list_index:#checks not swaping same element
			first_random_list_index = random.randint(0,len(list)-1)
			second_random_list_index = random.randint(0,len(list)-1)
	random_first = list[first_random_list_index]
	random_second = list[second_random_list_index]
	#re-assigns members
	list[first_random_list_index] = random_second
	list[second_random_list_index] = random_first
	
	return first_random_list_index, second_random_list_index
	
def swap(list,(source_index, destination_index)):
	source = list[source_index]
	destination = list[destination_index]
	#re-assigns members
	list[source_index] = destination
	list[destination_index] = source
	
	return list	

		
def centered_text(string,(x,y)):
	string_print_moveto = '\n'+str(x)+' ' +str(y)+' moveto'
	r_move_adjustment = '\n('+str(string)+') stringwidth pop \n'+str(0)+' exch sub .5 mul 0 rmoveto '
	string_print = string_print_moveto+r_move_adjustment+'\n('+str(string)+') show'
	return string_print
	
def draw_rectangle((x_start,y_start),(x_end,y_end),empty_or_solid):
	if empty_or_solid == 0:
		fill = 'stroke'
	elif empty_or_solid == 1:
		fill = 'fill'
	print_rectangle = '\n'+str(x_start)+' '+str(y_start)+' moveto\n'+str(x_end)+' '+str(y_start)+' lineto\n'+str(x_end)+' '+str(y_end)+' lineto\n'+str(x_start)+' '+str(y_end)+' lineto\n'+str(x_start)+' '+str(y_start)+' lineto closepath '+fill
	return print_rectangle

def print_dict(dict, label='Dictionary'):
	print label # Seemed handy to go ahead and just make this part of the function.
	keys = dict.keys()
	keys.sort()
	width = reduce(max, map(len, keys)) + 1 # Sneak way to get maximum length.
	for key in keys:
		print '  %*s: %s' % (-width, key, dict[key]) # The "*" inserts spaces.
class inserter:
	def __init__(self, new = None, e = None, num = None):
		self.new = new or []
		
		def insert(self,e,num):
			num = num+1
			i = num
			comp = len(self.new)
			while i > comp:
				self.new.append('')
				comp+=1
			self.new[num-1] = e#self.new[num-1] + e
			return self.new
		insert(self,e,num)
#new = []		
def insert(e,num, new):
	num = num+1
	#global new
	i = num
	comp = len(new)
	while i > comp:
		new.append(None)
		comp+=1
	new[num-1] = e#new[num-1]+e
	return new
def strip_file(path_file):
	i = 0
	while i < len(path_file)-1:
		if path_file[i] == '/':
			locale = i
		i+=1
	cut_off = len(path_file)-2 - locale
	file = path_file[locale+1:]
	#print locale
	return file

def read_single_list_from_file(input_filename):
	return open(input_filename).readlines()[0]

def clip(value,(low,high)):
	if value >= high:
		return high
	elif value <= low:
		return low
	else:
		return value
def split_groups(list_of_lists, cut_off):#slightly_busted
	list_of_lists.sort(cmp)
	amount_of_master_members = (list_of_lists[-1][0][0][0]/cut_off)
	def make_list(anything):
		return [anything]
	master_list = map(make_list,(range(amount_of_master_members+1)))
	for e in list_of_lists:
		index = e[0][0][0]/cut_off
		master_list[index].insert(0,e)
	index = 0
	while index < len(master_list):
		if len(e) == 1:
			master_list.pop(index)
		index +=1
	index = 0
	while index < len(master_list):
		master_list[index].pop()
		index +=1
	index = 0
	while index < master_list.count([]):
		master_list.remove([])
		index +=1
	newm = []
	for e in master_list:
		if len(e) > 0:
			newm.append(e)
	return newm

def average(list_of_stuff):	
	def add(x,y):
		return x+y
	avg = reduce(add, list_of_stuff)/len(list_of_stuff)
	return avg

def extract_e_elements(list_of_shit):	
	new_d_list = []
	for e in list_of_shit:
		new_d_list.append(e[4])
	return new_d_list
	
def extract_d_elements(list_of_shit):	
	new_d_list = []
	for e in list_of_shit:
		new_d_list.append(e[3])
	return new_d_list
def extract_c_elements(list_of_stuff):
	new_b_list = []
	for e in list_of_stuff:
		new_b_list.append(e[2])
	return new_b_list

def index_sort(a,b):
	return cmp(a._index, b._index)
	
def bsort(a,b):
	return cmp(a[1],b[1])
def csort(a,b):
	return cmp(a[2],b[2])
def csort_reverse(a,b):
	return cmp(b[2],a[2])
def dsort(a,b):
	return cmp(a[3],b[3])
def dsort_reverse(a,b):
	return cmp(b[3],a[3])
def esort(a,b):
	return cmp(a[4],b[4])
def randsort(a,b):
	return  (random.randint(0,1)*2)-1

def average_sort(a,b):
	return cmp(average(a),average(b))
def average_e(list_of_stuff):
	return average(extract_e_elements(list_of_stuff))
def average_d(list_of_stuff):
	return average(extract_d_elements(list_of_stuff))
def average_d_sort(a,b):
	first_average_d = average(extract_d_elements(a))
	next_average_d = average(extract_d_elements(b))
	return cmp(next_average_d,first_average_d)
def average_c(list_of_stuff):
	return average(extract_c_elements(list_of_stuff))
def average_c_sort(a,b):
	first_average = average_c(a)
	next_average = average_c(b)
	return cmp(next_average,next_average)
def mult(a,b):
		return a*b
def add1(x):
		return x+1
def list_mult(number,a_list):
		index = 0
		newlist = []
		for e in a_list:
			value = e*number                        
			newlist.append(value)
			index += 1
		return newlist
		
def remove_grouping(matrix):
	new = []
	for group in matrix:
		for e in group:
			new.append(e)
	return new



	
def drunk_list((min,max),step,length):
	middle = int(round((max-min)*.5))
	value = middle
	newlist = []
	i = 0
	while i < length:
		drunk_add = random.randint(0, step)
		if value + drunk_add >= max:
			direction = 0
		if value - drunk_add <= min:
			direction = 1
		else:
			direction = random.randint(0,1)
		
		if direction == 0:
			value = value - drunk_add
		if direction == 1:
			value = value + drunk_add
		value = clip(value,(min,max))
		newlist.append(value)
		i+=1
	return newlist

def amplitude_to_dB(amp):
	import math
	return 	20.*math.log10(amp)

def swap_one_permute(list):
	import permute
	return permute.permute_list(list)

	
def urn(number_of_elements, list_of_ints = range(20)):#fuck this implementation!
    if(number_of_elements > len(list_of_ints)):
        return 0
    pickArr = []
    tempArr = list_of_ints
    i = 0
    while(i < number_of_elements):
        g = Random()
        pickArr.append(tempArr[int(round((len(tempArr) - 1) * g.random()))])
        temp = pickArr[len(pickArr)-1]
        count = 0
        for x in tempArr:
            if(x == temp):
                tempArr[count] = 'null'
                tempArr2 = []
                for y in tempArr:
                        if(y != 'null'):
                                tempArr2.append(y)
                tempArr=tempArr2;
                break
            count = count + 1
        i = i + 1
    return pickArr

def urn(how_many, out_of = None):
	if not out_of:
		out_of = how_many
	a = range(out_of)
	a.sort(randsort)
	return a[0:how_many]

def slice_an_amount_randomly(amount, num_of_slices):
	chops = urn(num_of_slices-1, amount)
	chops.append(amount)
	chops.sort(cmp)
	chops.insert(0,0)
	slice_points = []
	accum = 0
	i =0
	while i < len(chops)-1:
		current_point = chops[i+1] - chops[i]
		accum+=chops[i]
		slice_points.append(current_point)
		i+=1
	return slice_points#, chops
		
		
def random_steps(amount, num_of_steps):
	all = slice_an_amount_randomly(amount, num_of_steps)
	new_all = []
	counter = 0
	for e in all:
		new_all.append(e+counter)
		counter+=e
	return new_all
		
	
def random_lengths_between_steps(amount, num_of_steps):
	pair_list = []
	ran_step_list = random_steps(amount, num_of_steps)
	i = 0
	while i < len(ran_step_list)-1:
		current = ran_step_list[i]
		future = ran_step_list[i+1]
		end = random.randint(current, future)
		pair_list.append([current, end])
		i+=1
	return pair_list
	
def flag_redundancies(list):
	new_thing = ''
	selected = []
	i = 1
	while i < len(list):
		if list[i] != new_thing:
			new_thing = list[i]
		if list[i-1] != new_thing:
			selected.append([list[i],i])
		i+=1
	return selected
	
def factorial(n):
    import math
    if not n >= 0:
        raise ValueError("n must be >= 0")
    if math.floor(n) != n:
        raise ValueError("n must be exact integer")
    if n+1 == n:  # catch a value like 1e300
        raise OverflowError("n too large")
    result = 1
    factor = 2
    while factor <= n:
        try:
            result *= factor
        except OverflowError:
            result *= long(factor)
        factor += 1
    return result
def divides_evenly(num,den):
	return (float(num))/(float(den)) == (int(num))/(int(den))
