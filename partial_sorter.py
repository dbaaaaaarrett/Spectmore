#!/usr/bin/python

import putil, sys, string, math
def read_sdif(input_filename):
	number_of_lines = 0
	for line in open(input_filename).readlines():
		words = line.strip().split()
		if len(words) == 6:
			number_of_lines += 1
	count = 0
	sdif_list = range(number_of_lines-1)
	for line in open(input_filename).readlines():
		words = line.strip().split()
		if len(words) == 12:
			timecomma = words[7]
			sometime = timecomma[0:7]
			atime = float(sometime)
		if len(words) == 6 and words[0] != '---First':
			partial = float(words[0])
			pitch = float(words[1])
			gain = float(words[2])
			phase = float(words[3])
			x = atime
			y = pitch
			data = [int(partial), x,  y, gain, phase]
			sdif_list[count] = data
			count +=1
	return sdif_list
a = 'list of partials'
a = []
def extract_partials(matrix,which_partial):
	new = []
	for e in matrix:
		if e[0] == which_partial:
			new.append(e)
	return new
	
def sort_matrix_by_partial_nums(matrix):
	output = []
	index = 0
	while index <= matrix[-1][0]:
		output.append(extract_partials(matrix,index))
		index+=1
	return output

def extract_time_chunks(matrix,what_time):
	new = []
	for e in matrix:
		if float(e[1]) > float(what_time)-.0000001 and float(e[1]) < float(what_time)+.0000001:
			new.append(e)
	
	return new

def sort_matrix_by_time(matrix,interval):
	output = []
	index = 0
	while index <= matrix[-1][1]*(1./interval):
		output.append(extract_time_chunks(matrix,float(index*interval)))
		index+=1
	output.reverse
	return output

def bsort(a,b):
	return cmp(a[1],b[1])
def csort(a,b):
	return cmp(a[2],b[2])
	
def get_increments(matrix):
	matrix.sort(bsort)
	increment_list = []
	index = 0
	while index < len(matrix)-1:
		#if matrix[index][1] != matrix[index+1][1]:
		increment = matrix[index+1][1]- matrix[index][1]
		if increment != 0.0:
			increment_list.append(increment)
		index+=1
	increment_list.sort(cmp)
	return increment_list

#smallest_increment = get_increments(matrix)[0]
	
def remove_short_partials(matrix,smallest_length):
	shortened_matrix = []
	for partial in matrix:
		partial_length = partial[-1][1] - partial[0][1]
		if partial_length >= smallest_length:
			shortened_matrix.append(partial)
	return shortened_matrix

	

def remove_soft_partials(matrix,smallest_average_amplitude):			
	shortened_matrix = []
	for partial in matrix:
		amplitudes_added = 0
		for e in partial:
			amplitudes_added = amplitudes_added+e[3]
		average_amplitude = amplitudes_added/len(partial)
		if average_amplitude >= smallest_average_amplitude:
			shortened_matrix.append(partial)
		#list_of_average_amplitudes.append(average_amplitude)
	return shortened_matrix
	
def remove_grouping(matrix):
	new = []
	for group in matrix:
		for e in group:
			new.append(e)
	return new

def line(go_from,to,in_how_many_steps):
	step_amount = (to - go_from)/(float(in_how_many_steps))
	line_vals = []
	index = 0
	while index < in_how_many_steps:
		current_val = index*step_amount
		line_vals.append(current_val)
		index += 1
	return line_vals
	
def concat_lists(lista,listb):
	newlist = []
	index = 0
	while index < len(lista):
		newlist.append([lista[index],listb[index]])
	return newlist
def populate_partial_times(partial):
	index = 1
	while index < len(partial):
		start = partial[index]
		stop = partial[index-1]
		gap = start[1] - stop[1]
		num_of_points_for_gap = gap/smallest_increment
		interpolated_times = line(start[1],stop[1],num_of_points_for_gap)
		interpolated_freqs = line(start[2],stop[2],num_of_points_for_gap)
		interpolated_times_freqs = concat_lists(interpolated_times,interpolated_freqs)
		#j = 0
		#while j < (gap/smallest_increment):
			
		index += 1
	return interpolated_times_freqs

#create ftom
#accumulator for x position-minumum x distance...

#round((12*math.log((float(f)/base_a4),2)+69.)*2.)

#def frequency_to_twenty_four(frequency,base_a4=440):
#	return round((12*math.log((float(frequency)/base_a4),2)+69.)*2.)*.5
#
#def frequency_to_twelve(frequency,base_a4=440):
#	return round((12*math.log((float(frequency)/base_a4),2)+69.))

#def frequency_to_twelve_plus_cents(frequency,base_a4=440):
#	midi_float = 12*math.log((float(frequency)/base_a4),2)+69.
#	midi_round = round(midi_float)
#	cents_deviation = (midi_float-midi_round)*100
#	return midi_round,cents_deviation
	
#def midi_to_note_and_octave(midi_note,middle_c=60):
#	octave = int((midi_note-middle_c)/12)
#	note = 	midi_note%12
#	return [note, octave]
		
def frequency_to_note_and_octave(frequency, twenty_four_or_twelve=0, base_a4=440,middle_c=60):
	if twenty_four_or_twelve == 0:
		return midi_to_note_and_octave(frequency_to_twenty_four(frequency,base_a4),middle_c)
	elif twenty_four_or_twelve == 1:
		return midi_to_note_and_octave(frequency_to_twelve(frequency,base_a4),middle_c)

def total_sort():
	input_filename = str(sys.argv[1])
	partial_threshold = float(sys.argv[2])
	resample_factor = float(sys.argv[3])
	matrix = read_sdif(input_filename)
	partials = sort_matrix_by_partial_nums(matrix)
	loud_partials = remove_soft_partials(partials,partial_threshold)
	def collect_amount_of_partials(list_of_partials):
		lengths = []
		for e in list_of_partials:
			lengths.append(len(e))
		return lengths
	no_group = remove_grouping(loud_partials)
	times = sort_matrix_by_time(no_group,resample_factor)
	print collect_amount_of_partials(times),'partials per group'
	pitch_org_of_times = []
	print len(times),'times'
	for e in times:
		e.sort(csort)
		pitch_org_of_times.append(e)
	return pitch_org_of_times

def total_sort_sdif(partial_list,resampling_interval):
	
	#partials = sort_matrix_by_partial_nums(partial_list)
	#loud_partials = remove_soft_partials(partials,partial_threshold)
	def collect_amount_of_partials(list_of_partials):
		lengths = []
		for e in list_of_partials:
			lengths.append(len(e))
		return lengths
	no_group = remove_grouping(partial_list)
	times = sort_matrix_by_time(no_group,resampling_interval)
	#print times
	print collect_amount_of_partials(times),'partials per group'
	pitch_org_of_times = []
	print len(times),'times'
	for e in times:
		e.sort(csort)
		#print e
		if len(e) > 0:
			pitch_org_of_times.append(e)
	return pitch_org_of_times
	
#input_filename = str(sys.argv[1])
#partial_threshold = float(sys.argv[2])
#resample_factor = float(sys.argv[3])
#matrix = read_sdif(input_filename)
#times = sort_matrix_by_time(matrix,resample_factor)
#print times,'times'
#if len(sys.argv) > 2:
#	page = open('/print/zBU/old/final_time_list_b2_.25.py', 'w')
#	page.write('def return_list():\n\treturn '+str(total_sort()))
