#!/usr/bin/python
# -*- coding: UTF-8-*-
#NOTE---def get_beam_and_note_data should be reconsidered and
	#put in main maybe


import path, sys, string, putil, random, partial_sorter, pages, preferences


path_file = path.path_file

page_width = preferences.page_width
page_height = preferences.page_height
page_length = page_height

#each staff space = 3 points
#accidentals are 3 points too low and need to been 9 points left of note
set_maestro_percussion = '\n/MaestroPercussion findfont \n24 scalefont\nsetfont'
set_maestro = '\n/Maestro findfont \n24 scalefont\nsetfont'
set_times = '\n/TimesNewRomanPSMT findfont \n11 scalefont\nsetfont'
note_up = '\n(q) show'
note_down = '\n(Q) show'
note_head = '\n(Ï) show'
harmonic = '\n(á) show'
sharp = '\n(#) show'
natural = '\n(n) show'
quarter_tone_flat = set_maestro_percussion+'\n(B) show'+set_maestro
quarter_tone_sharp = set_maestro_percussion+'\n(µ) show'+set_maestro
flat = '\n(b) show'
beam = '\n(·) show'
barlines = '\n(=) show'
ledger = '\n (_) show'
g_clef = '\n(&) show'
bass_clef = '\n(?) show'
alto_clef = '\n(B) show'
percussion_clef = '\n(‹) show'
parenthesis = '\n((         )) show'



staff_offset = 12 #pts
spacing = 3 #pts
ledger_spacing = spacing*2
line_spacing = ledger_spacing
above_staff = (spacing*9)-3
below_staff = -9

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
		
def twelve_tone_index(index, octave, sharps_or_flats):
	#sharps_favored = [(1, 0), (1, 1), (2, 0), (2, 1), (3, 0), (4, 0), (4, 1),(5, 0) (5, 1), (6, 0), (6, 1), (7, 0)]
	#flats_favored = [(1, 0), (2, -1), (2, 0), (3, -1), (3, 0), (4, 0), (5, -1), (5, 0), (6, -1), (6, 0), (7, -1), (7, 0)]
	
	ascending_24_tone = [(1, 0),(1, .5),(1, 1),(2, -.5),(2, 0),(2, .5),(2, 1),(3, -.5),(3, 0),(3, .5),(4, 0), (4, .5),(4, 1),(5, -.5),(5, 0),(5, .5),(5, 1), (6, -.5), (6, 0),(6, .5), (6, 1), (7, -.5),(7, 0),(7, .5)]
	descending_24_tone = [(1, 0),(1, .5),(2, -1),(2, -.5),(2, 0),(2, .5),(3, -1),(3, -.5),(3, 0),(4, -.5),(4, 0), (4, .5),(5, -1),(5, -.5),(5, 0),(5, .5),(6, -1), (6, -.5), (6, 0),(6, .5), (7, -1), (7, -.5),(7, 0),(8, -.5)]

	if sharps_or_flats == 1:
		acc = ascending_24_tone#sharps_favored
	elif sharps_or_flats == -1:
		acc = descending_24_tone#flats_favored
	note = acc[int(index*2.0)]
	transposition = octave*7
	note_and_accidental_status = note[0]+transposition, note[1]
	return note_and_accidental_status
def clef_offsets(clef):
	if clef == g_clef:
		y_offset = 0
	if clef == alto_clef:
		y_offset = 18
	if clef == bass_clef:
		y_offset = 36
	else:
		y_offset = 0
	return y_offset
one_space = 3
#not used	
def xy_offset(point_and_acc):
	x_offset = abs(point_and_acc[1]*9) #makes 9 pt shift of note from accidental
	y_offset = (point_and_acc[0]-1)*3
	accidental_status = point_and_acc[1]
	return x_offset, y_offset, accidental_status

def put_on_notes(x_pos, note_and_accidental_status, up_down,(clef,transpose)):
	
	note = note_and_accidental_status[0]
	accidental_status = note_and_accidental_status[1]
	clef_offset = clef_offsets(clef)
	#print clef
	#print clef_offset, 'clef offset'
	y_pos = ((note)*spacing) - staff_offset + clef_offset + (transpose*one_space)#<--this is where transposition must occur
	#staff spacing is 3 points and starting pitch is treble 'f'(hence 9pt transp.)
	#accidentals are offset by 3 y points
	def ledger_line(y_pos):
		ledger_count = 0
		if y_pos <= below_staff:
			distance_from_bottom = y_pos+below_staff
			ledger_count = int(((y_pos-below_staff-spacing)/ledger_spacing))#divides difference of space b/t staff&note
		elif y_pos >= above_staff:
			ledger_count = (abs((y_pos-above_staff+spacing)/ledger_spacing))
		return ledger_count#positive values=#of ledgers above, ditto for negatives, 0=none
	def put_on_ledger_lines(ledger_count):
		if ledger_count > 0:
			ledger_position = (line_spacing*(ledger_count))+above_staff
		elif ledger_count < 0:
			ledger_position = (line_spacing*(ledger_count))
		else:	ledger_position = 0
		return ledger_position
	
	
	#handles note and accidental
	accidental_offset = 9
	
	#print type(up_down)
	if up_down == 1:
		stem = note_up
		y_bias = 0
		x_bias = 0
	elif up_down == -1:
		stem = note_down
		y_bias = 0
		x_bias = 0
	elif up_down == 0 or 'normal':
		stem = note_head
		y_bias = 3
		x_bias = 0
	elif up_down == 'harmonic':
		stem = harmonic
		y_bias = 3
		x_bias = 0
	if up_down == 2:
		stem = parenthesis
		y_bias = 0
		x_bias = -13
	if type(up_down) == str and up_down != 'normal' and up_down != 'harmonic':
		stem = set_times+'\n('+up_down+') show'+set_maestro
		y_bias = 3
		x_bias = -4
	#if accidental_status == 0:	#use this if i ever decide not to use natural sign on natural notes
	#	x_offset = 0
	#	x_pos_note = x_pos+x_offset
	#	print_note = '\n'+ str(x_pos+x_bias)+' '+ str(y_pos+y_bias)+' 0 m ' + stem
	#	result = print_note
	if accidental_status == 0:
		accidental_to_use = natural
		accidental_offset = 9

	elif accidental_status == 1:
		accidental_to_use = sharp
	elif accidental_status == -1:
		accidental_to_use = flat
	elif accidental_status == .5:
		accidental_to_use = quarter_tone_sharp
	elif accidental_status == -.5:
		accidental_to_use = quarter_tone_flat
		
	x_offset = accidental_offset
	x_pos_note = x_pos+x_offset
	print_accidental = '\n'+ str(x_pos)+' '+ str(y_pos+spacing)+' 0 m ' + accidental_to_use
	print_note = '\n'+ str(x_pos+9+x_bias)+' '+ str(y_pos+y_bias)+' 0 m ' + stem
	result = print_accidental + print_note
	#handles ledger lines

	def add1(x):
		return x+1
	
	def neg_pos(x):
		if x < 0:
			return -1
		if x >= 0:
			return 1
	ledger_count = ledger_line(y_pos)
	if ledger_count != 0:
		ledger_side = neg_pos(ledger_count)
		inclusive_ledgers = map(add1,range(abs(ledger_count)))
		inclusive_ledgers = list_mult(ledger_side, inclusive_ledgers)#applies positive or negativeness
		multi_ledger_pos = map(put_on_ledger_lines, inclusive_ledgers)
		def print_ledgers(ledger_pos, x_pos):
			if ledger_count != 0:
				x_pos = x_pos+x_offset-1
				print_ledger = 	'\n'+ str(x_pos)+' '+ str(ledger_pos)+' 0 m ' + ledger
			else:	print_ledger = ''
			return print_ledger
       
		index = 0
		print_ledger_lines = []
		for e in multi_ledger_pos:
			ledger_string = print_ledgers(e, x_pos)                       
			#print_ledger_lines = ledger_string+ledger_string
			print_ledger_lines.append(ledger_string)
			index += 1
	else:	print_ledger_lines = []
	
	y_pos = y_pos + y_bias
	x_pos_note = x_pos_note
	x_y_pos = x_pos_note, y_pos
	print_ledger_lines = string.joinfields(print_ledger_lines,'')
	return result + print_ledger_lines, x_y_pos

def note_entry(time, note, octave, sharp_flat, stem,(clef,transpose)):
	note = put_on_notes(time, twelve_tone_index(note,octave,sharp_flat), stem,(clef,transpose))
	return note[:]


def generate_staff(position, length):
	staff_line_width = .5
	print_line_width = '\n'+ str(staff_line_width) +' slw'
	total_line_locales = list_mult(line_spacing,range(5))
	length = length
	x_start = position[0]
	y_start = position[1]
	x_end = x_start+length
	
	def print_total_staves(line_locale):
		print_line_moveto = '\n'+str(x_start)+ ' '+ str(line_locale+y_start) + ' moveto '
		print_line_lineto = '\n'+str(x_end)+' '+str(line_locale+y_start) + ' lineto stroke'
		return print_line_moveto+print_line_lineto
	print_all_lines = map(print_total_staves,total_line_locales)
	print_all_lines = string.joinfields(print_all_lines,'')
	return print_line_width+print_all_lines

staff_spacing = 100

x_offset = 100
left_right_margin = x_offset/2
staff_width = page_width - left_right_margin*2
clef_indent = 12
num_of_staves = preferences.num_of_staves#14#page_height/86#86 is really staff spacing!!
staff_spacing = page_length/(num_of_staves)
staff_time = staff_width-clef_indent*2
total_time_on_page = staff_time*num_of_staves
print_line_length = page_width-x_offset

def generate_staves(how_many, x_offset):	
	margin_factor_of_staff_spacing = .5
	staff_spacing = page_length/(how_many+margin_factor_of_staff_spacing*1)#co-denpendent w/ notes_on_staves
	top_bottom_margin = staff_spacing*(margin_factor_of_staff_spacing*2)
	print_staves = []
	index = 0
	while index < how_many:
		print_staff_y = (page_length - (top_bottom_margin))-(index*staff_spacing)
		position = left_right_margin, print_staff_y
		print_staves.append(generate_staff(position, print_line_length))
		index += 1
	print_staves = string.joinfields(print_staves,'')
	return print_staves, staff_spacing, top_bottom_margin 

staff_spacing = generate_staves(num_of_staves, x_offset)[1]
top_bottom_margin = generate_staves(num_of_staves, x_offset)[2]

beam_up_baseline = 44#not used
beam_down_baseline = -20#not used
shortest_stem_length = 20

def draw_stem(x_y_start,up_down, y_draw_to):
	stem_thickness = .5
	print_stem_width = '\n'+ str(stem_thickness) +' slw'
	x_start = x_y_start[0]
	y_start = x_y_start[1]
	if up_down == 1:
		target = y_draw_to#+.5
		x_start = x_start + 7.5
		y_start = y_start + .5
	elif up_down == 0:
		target = y_draw_to
		x_start = x_start + .25
	print_start = '\n'+str(x_start)+' ' + str(y_start)+ ' ' + 'moveto'
	print_end = '\n'+str(x_start)+' ' + str(target)+ ' ' + 'lineto stroke'
	x_y_start = x_start, y_start
	return print_stem_width+print_start+print_end, x_y_start

def get_x_y_coords_from_notes(list_of_notes_with_vals):
	list_of_x_y_coords = []
	for e in list_of_notes_with_vals:
		x_y_coords = note_entry(e[0],e[1],e[2],e[3],e[4],e[5])[1]
		list_of_x_y_coords.append(x_y_coords)
	return list_of_x_y_coords

def get_x_y_vals(x_y_vals, x_or_y):
		single_val_list = []
		for e in x_y_vals:
			single_val_list.append(e[x_or_y])
		return single_val_list	
def average(list_of_stuff):	
	def add(x,y):
		return x+y
	avg = reduce(add, list_of_stuff)/len(list_of_stuff)
	return avg

def draw_arrow((start_x,start_y), (height, length),dent=2):
	dent = .2*length
	go_down = start_x, start_y-(height*.5)
	r_tip = start_x+length,start_y
	go_up = start_x, start_y+(height*.5)
	print_arrow = '\nnewpath '+str(start_x)+' '+str(start_y)+' moveto\n'+str(go_down[0]-dent)+' '+str(go_down[1])+' lineto\n'+str(r_tip[0])+' '+str(r_tip[1])+' lineto\n'+str(go_up[0]-dent)+' '+str(go_up[1])+' lineto\n'+str(start_x)+' '+str(start_y)+' lineto closepath fill\n'
	return print_arrow
	
minimun_beam_distance = 15
beam_directions = []
def stemmed_group_of_notes(list_of_x_y_vals, extend_l_r,(to_l_margin,to_r_margin)):
	
	left_extension = extend_l_r[0]
	right_extension = extend_l_r[1]
	list_of_y_vals = get_x_y_vals(list_of_x_y_vals, 1)
	break_point = 9
	def tsort(a, b):
		return cmp(a[1], b[1])
	#beaming
	beam_thickness = 3
	print_beam_width = '\n'+ str(beam_thickness) +' slw'
	first_x = list_of_x_y_vals[0]
	last_x = list_of_x_y_vals[-1]
	list_of_x_y_vals.sort(tsort)
	highest_y_val = list_of_x_y_vals[-1][1]
	lowest_y_val = list_of_x_y_vals[0][1]
	
	def determine_direction(list_of_y_vals):
		average_y_pos = average(list_of_y_vals)
		if average_y_pos >= break_point:
			direction = 0
		else:  direction = 1
		return direction
	direction = determine_direction(list_of_y_vals)
	
	if direction == 1:
		y_draw_to = highest_y_val+shortest_stem_length
		if y_draw_to < break_point+minimun_beam_distance+6:
			y_draw_to =  break_point+minimun_beam_distance
	elif direction == 0:
		y_draw_to = lowest_y_val-shortest_stem_length
		if y_draw_to > break_point-minimun_beam_distance+6:
			y_draw_to =  break_point-minimun_beam_distance-6
	all_stems = []
	for x_y_vals in list_of_x_y_vals:
		print_stems = draw_stem(x_y_vals,direction,y_draw_to)[0]
		all_stems.append(print_stems)
	
	all_stems = string.joinfields(all_stems,'')
	
	beam_locale = y_draw_to
	location_data = [[direction,beam_locale],list_of_x_y_vals]
	beam_directions.append(location_data)
	
	#x_beam_start = x_beam_start
	#x_beam_end = x_beam_end+right_extension
	if to_l_margin == 1:
		x_beam_start = 0
		left_extension = 0
	else: 
		left_extension = extend_l_r[0]
		x_beam_start = draw_stem(first_x,direction,y_draw_to)[1][0]
	if to_r_margin == 1:
		x_beam_end = staff_time+(clef_indent)#-(left_right_margin+clef_indent)
		right_extension = 0
		arrow = draw_arrow((x_beam_end,y_draw_to),(7,7))
	else: 
		right_extension = extend_l_r[1]
		x_beam_end = draw_stem(last_x,direction,y_draw_to)[1][0]
		arrow = ''
	print_beam = '\n'+str(x_beam_start+left_extension)+' '+str(y_draw_to)+ ' '+'moveto'+'\n'+ str(x_beam_end+right_extension)+ ' '+str(y_draw_to)+' lineto stroke'+arrow
	
	return all_stems+print_beam_width+print_beam,location_data

def beamed_and_stemmed_from_note_group(list_of_notes_and_vals,extend_l_r,(to_l_margin,to_r_margin)):
	x_y_coords = get_x_y_coords_from_notes(list_of_notes_and_vals)
	return stemmed_group_of_notes(x_y_coords,extend_l_r,(to_l_margin,to_r_margin))[0]

def get_location_data_from_note_group(list_of_notes_and_vals):
	x_y_coords = get_x_y_coords_from_notes(list_of_notes_and_vals)
	return stemmed_group_of_notes(x_y_coords,(0,0),(0,0))[1]


def get_offsets(absolute_time,(which_staff,staff_count)):
		staves_per_page = num_of_staves/staff_count
		mod_pages = ((absolute_time%(total_time_on_page/staff_count))), int((absolute_time/(total_time_on_page/staff_count)))
		current_page_time = mod_pages[0]
		mod_staves = (current_page_time%(staff_time)), int(current_page_time/(staff_time))
		x_offset = mod_staves[0]
		y_offset = (page_length-top_bottom_margin) - ((mod_staves[1]*staff_spacing*staff_count)+(which_staff*staff_spacing))
		return x_offset, y_offset, current_page_time,mod_pages, current_page_time, mod_staves
def notes_on_staves(time, note, octave, sharp_flat, stem,(clef,transpose),(which_staff,staff_count)):
	#mod_pages = (time%total_time_on_page), int(time/total_time_on_page)
	#current_page_time = mod_pages[0]
	#mod_staves = (current_page_time%(staff_time)), int(current_page_time/(staff_time))
	#x_offset = mod_staves[0]
	#y_offset = (page_length-top_bottom_margin) - (mod_staves[1]*staff_spacing)
	
	
	x_offset, y_offset, current_page_time,mod_pages, current_page_time, mod_staves = get_offsets(time,(which_staff,staff_count))[0],get_offsets(time,(which_staff,staff_count))[1],get_offsets(time,(which_staff,staff_count))[2],get_offsets(time,(which_staff,staff_count))[3],get_offsets(time,(which_staff,staff_count))[4],get_offsets(time,(which_staff,staff_count))[5]
	page_num = mod_pages[1]+1
	place_notes = '\n0 0 translate \n gsave \n'+str(clef_indent+left_right_margin)+' '+str(y_offset) +' '+ 'translate'+ note_entry(x_offset, note, octave, sharp_flat, stem,(clef,transpose))[0] + '\ngrestore'
	place_notes = string.joinfields(place_notes,'')
	pages.insert(place_notes,page_num)
	#pages = open(path_file+str(page_num)+'.ps', 'a')
	#pages.write(place_notes)
#extension = -15,15
#last_note_length = 7

def beamed_on_staves(list_of_notes_and_vals, (which_beamed_group, out_of_how_many),last_note_length,(which_staff,staff_count)):
	l_extension = 0#inits
	r_extension = 0
	list_of_notes_and_vals.sort(cmp)
	time = list_of_notes_and_vals[0][0]
	last_note = list_of_notes_and_vals[-1]
	last_note_time = list_of_notes_and_vals[-1][0]
	
	x_offset, y_offset, current_page_time,mod_pages, current_page_time, mod_staves = get_offsets(time,(which_staff,staff_count))[0],get_offsets(time,(which_staff,staff_count))[1],get_offsets(time,(which_staff,staff_count))[2],get_offsets(time,(which_staff,staff_count))[3],get_offsets(time,(which_staff,staff_count))[4],get_offsets(time,(which_staff,staff_count))[5]

	beam_to_end_of_staff = staff_time - (last_note_time%staff_time)
	if which_beamed_group == 0:
		l_extension = 0
		to_l_margin = 0

		if out_of_how_many > 1:
			to_r_margin = 1
		else:
			to_r_margin = 0
			r_extension = last_note_length

	#elif which_beamed_group < out_of_how_many-1:
	#	to_r_margin = 1
	#	to_l_margin = 1
	elif which_beamed_group == out_of_how_many-1:
		r_extension = last_note_length
		to_r_margin = 0
		if out_of_how_many > 1:
			to_l_margin = 1
		else:
			to_l_margin = 0
	
	elif which_beamed_group < out_of_how_many -1 and out_of_how_many > 1:
		#print which_beamed_group,'which!!!'
		to_r_margin = 1#should be 1
		to_l_margin = 1
	else:
		r_extension = last_note_length
		to_r_margin = 0
		to_l_margin = 0
	extend_l_r = l_extension, r_extension
	#print to_l_margin, 'to l',to_r_margin,'to r'
	for e in list_of_notes_and_vals:
		notes_on_staves(e[0],e[1],e[2],e[3],e[4],e[5],(which_staff,staff_count))
	for e in list_of_notes_and_vals:
		unwrapped_time = e[0]
		e[0] = unwrapped_time%staff_time
	beams_and_stems = '\n0 0 translate \n gsave \n'+str(clef_indent+left_right_margin)+' '+str(y_offset) +' '+ 'translate'+ beamed_and_stemmed_from_note_group(list_of_notes_and_vals,(extend_l_r),(to_l_margin,to_r_margin)) + '\ngrestore'
	page_num = mod_pages[1]+1
	#print page_num, list_of_notes_and_vals[0]
	#print page_num#, mod_pages#/(total_time_on_page/staff_count)
	pages.insert(beams_and_stems,page_num)
	#pages = open(path_file+str(page_num)+'.ps', 'a')
	#pages.write(beams_and_stems)
	
def split_groups(list_of_lists, cut_off):#slightly_busted
	list_of_lists.sort(cmp)
	amount_of_master_members = (list_of_lists[-1][0]/cut_off)
	def make_list(anything):
		return [anything]
	master_list = map(make_list,(range(amount_of_master_members+1)))
	for e in list_of_lists:
		index = e[0]/cut_off
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
def beam_and_note_head_data(list_of_lists_of_notes,(which_staff,staff_count)):
	list_of_lists_of_lists_of_notes = split_groups(list_of_lists_of_notes, staff_time)
	beam_and_note_data = []
	for list_of_notes in list_of_lists_of_lists_of_notes:
		beam_and_note_data.append(get_location_data_from_note_group(list_of_notes))
	return beam_and_note_data
	
def multi_group_beamed_notes(list_of_lists_of_notes, last_note_length,(which_staff,staff_count)):
	#print beam_and_note_head_data(list_of_lists_of_notes,(which_staff,staff_count))
	list_of_lists_of_lists_of_notes = split_groups(list_of_lists_of_notes, staff_time)
	last_note = list_of_lists_of_notes[-1]
	last_note_time = last_note[0]

	index = 0

	end_beam_time = last_note_time+last_note_length
	note_head_locale = get_offsets(last_note_time,(which_staff,staff_count))[0]
	total_end_point = note_head_locale+last_note_length
	total_wraps = get_offsets(total_end_point,(which_staff,staff_count))[5][1]#IS THIS broken???
	end_wrap_time = get_offsets(total_end_point,(which_staff,staff_count))[5][0]
	pages_used = get_offsets(total_end_point,(which_staff,staff_count))[3]
	#total_wraps = (total_end_point-note_head_locale)/staff_time
	def beam_wrap(last_note, r_extension):
		index = 0
		def starts_and_end(total_end_point):
			num_of_wraps = (note_head_locale+r_extension)/staff_time
			list_total_wraps = range(num_of_wraps)
			index = 0
			list_of_times = []
			while index <= num_of_wraps:
				current_wrap = num_of_wraps-index
				if index == num_of_wraps:
					note = staff_time*(index)+((last_note_time/staff_time)*staff_time)#fix for multisavage
					end_length = end_wrap_time
					extension = 0
				elif index == 0:
					note = last_note_time
					end_length = 0
					extension = 1
				else:
					note = staff_time*(index)+((last_note_time/staff_time)*staff_time)#fix for multisavage
					end_length = 0
					extension = 1
				times = [note,end_length,extension]
				list_of_times.append(times)
				index +=1
			if num_of_wraps == 0:
				r = end_wrap_time
				l = last_note_time
				times = [l,r]
				list_of_times = [times]
			list_of_times.sort(cmp)
			
			#list_of_times.reverse
			return list_of_times
		return starts_and_end(total_end_point)
	
	wrapped_list = beam_wrap(last_note, last_note_length)
	note_extender = []
	for e in wrapped_list:
		note_entry = [e[0],last_note[1],last_note[2],last_note[3],last_note[4],last_note[5]]
		note_extender.append(note_entry)
	index = 0
	if int(total_wraps) != 0:
		last_note_length = note_extender[-1][1]
		beam_extension_constant = 1
	else:
		last_note_length = last_note_length
		beam_extension_constant = 0
	while index < len(note_extender)-1:
		end_wrap_time = note_extender[-1][1]
		enter_this_beamed_note = note_extender[index+1]#offset beams last note to end
		notes_on_staves(enter_this_beamed_note[0],enter_this_beamed_note[1],enter_this_beamed_note[2],enter_this_beamed_note[3],2,enter_this_beamed_note[5],(which_staff,staff_count))#adds parren
		beamed_on_staves([enter_this_beamed_note],(index+2,len(note_extender)+1),end_wrap_time,(which_staff,staff_count))#offsets take care of making it not first note in group
		index+=1
	
	def local_wraps(list_of_lists_of_lists_of_notes):#handles mid-group spill-over
		i = 0
		while i < len(list_of_lists_of_lists_of_notes)-1:#subtract one...
			index_ahead = list_of_lists_of_lists_of_notes[i+1][0]#weird, the last time is located at [0]...maybe a sort in the future
			index_current = list_of_lists_of_lists_of_notes[i][0]
			group_difference = index_ahead[0] - index_current[0]
			current_level = (index_current[0]/staff_time)*staff_time
			ahead_level = (index_ahead[0]/staff_time)*staff_time
			level_difference = ahead_level - current_level
			num_wraps = level_difference/staff_time
			if num_wraps > 1:
				j = 0
				while j < num_wraps-1:
					current_wraped_time = current_level+(j*staff_time)+staff_time
					current_wraped_member = [current_level+(j*staff_time)+staff_time,index_current[1],index_current[2],index_current[3],index_current[4],index_current[5]]
					current_alias = current_wraped_member
					notes_on_staves(current_alias[0],current_alias[1],current_alias[2],current_alias[3],2,current_alias[5],(which_staff,staff_count))#adds parren
					beamed_on_staves([current_wraped_member], (j+2,num_wraps+2),0,(which_staff,staff_count))

					if j == num_wraps-2:
						new_line_note = [ahead_level, index_current[1],index_current[2],index_current[3],index_current[4],index_current[5]]
						list_of_lists_of_lists_of_notes[i+1].insert(-1,new_line_note)
						notes_on_staves(new_line_note[0],new_line_note[1],new_line_note[2],new_line_note[3],2,new_line_note[5],(which_staff,staff_count))#adds parren
					j += 1 
			else:
				new_line_member = [current_level+staff_time,index_current[1],index_current[2],index_current[3],index_current[4],index_current[5]]
				list_of_lists_of_lists_of_notes[i+1].insert(-1,new_line_member)
				#print len(list_of_lists_of_lists_of_notes[i+1]),'LENGTH!!!!!'

				notes_on_staves(new_line_member[0],new_line_member[1],new_line_member[2],new_line_member[3],2,new_line_member[5],(which_staff,staff_count))#adds parren
			i += 1
	local_wraps(list_of_lists_of_lists_of_notes)

	index = 0
	while index < len(list_of_lists_of_lists_of_notes):
		how_many_groups_of_notes = len(list_of_lists_of_lists_of_notes)+beam_extension_constant
		#print index,'index',how_many_groups_of_notes,'how many',last_note_length,'last note'
		#print index,how_many_groups_of_notes
		#if len(list_of_lists_of_lists_of_notes[index]) >= 1:#cheap fix...look into this without the len test
		beamed_on_staves(list_of_lists_of_lists_of_notes[index],(index,how_many_groups_of_notes),last_note_length,(which_staff,staff_count))
		index +=1
	#print 'successfully beamed!'
		
	
def staves_on_pages(num_of_pages):
	place_staves = generate_staves(num_of_staves,x_offset)[0]
	place_staves = string.joinfields(place_staves,'')
	index = 0
	while index < num_of_pages:
		page_num = index + 1
		pages = open(path_file+str(page_num)+'.ps', 'a')
		pages.write(place_staves)
		index += 1
#list = [[[staff_name,cleff][staff_name,cleff]],[[staff..,...],[]]]...	
#sample_staff_list = [[['Piano',g_clef],['Piano',bass_clef]],[['Violin',g_clef]],[['Viola',alto_clef]]]
#sample_staff_list = [[['piano_treble',g_clef]]]
def count_staves_from_systems(list_of_systems):
		index = 0
		for system in list_of_systems:
			index = index + len(system)
		amount_of_staves = index
		return amount_of_staves

def generate_instrument_staves(list_of_systems,num_of_pages):
	
	amount_of_staves = count_staves_from_systems(list_of_systems)
	number_of_systems = num_of_staves/amount_of_staves#make sure amount of staves is multiple  of...
	
def generate_clefs(list_of_system_info): 
	return 0

def generate_clef(position, which_clef):
	x_start = position[0]
	y_start = position[1]
	if which_clef == g_clef:
		y_offset = 6
	if which_clef == bass_clef:
		y_offset = 18
	if which_clef == alto_clef:
		y_offset = 12
	if which_clef == percussion_clef:
		y_offset = 6
	print_clef_moveto = '\n'+str(x_start+2.5)+ ' '+ str(y_start+y_offset) + ' moveto '
	print_clef_draw = str(which_clef)
	return str(print_clef_moveto)+print_clef_draw

	
def draw_group_brackets(list_of_lists_of_clefs,x_offset,page_offset_index):
	j = 0
	print_group_brackets = []
	print_names = []
	#print list_of_lists_of_clefs
	constant = 0
	while j < len(list_of_lists_of_clefs):
		#clef = single_list_of_staves[j][1]
		group = list_of_lists_of_clefs[j]
		page_offset = page_offset_index*staff_spacing*amount_of_staves
		print_line_y = (page_length - (top_bottom_margin))-((j+constant)*staff_spacing+page_offset)
		position_y_top = print_line_y+24
		position_x = left_right_margin
		position_y_bottom = position_y_top-((len(group)-1)*staff_spacing)-24
		bracket_width = 1
		
		print_line_width = '\n'+ str(bracket_width) +' slw'
		print_top_moveto = '\n'+str(position_x)+ ' '+ str(position_y_top) + ' moveto '
		print_bottom_draw = '\n'+str(position_x)+ ' '+ str(position_y_bottom) + ' lineto stroke '
		
		print_moveto_name = '\n'+str(position_x-35)+ ' '+ str(((position_y_top+position_y_bottom)/2)-3) + ' moveto '
		r_move_adjustment = '\n('+group[0][0]+') stringwidth pop \n'+str(left_right_margin/2)+' exch sub 0 rmoveto '#right-aligns the name text
		print_name = '\n('+group[0][0]+') show'
		
		print_names.append(set_times+print_moveto_name+r_move_adjustment+print_name+set_maestro)
		print_group_brackets.append(print_line_width+print_top_moveto+print_bottom_draw)
		j+=1
		constant += len(group)-1#an incrementer to account for the length of multi-staved systems
		#print_group_brackets = string.joinfields(print_group_brackets,'')
	return print_group_brackets+print_names
		
def generate_clefs(list_of_lists_of_clefs, x_offset):	
	margin_factor_of_staff_spacing = .5
	#staff_spacing = page_length/(how_many+margin_factor_of_staff_spacing*1)#co-denpendent w/ notes_on_staves
	top_bottom_margin = staff_spacing*(margin_factor_of_staff_spacing*2)
	print_clefs = []
	index = 0
	def single_list(list_of_stuff):
		newlist = []
		for sublist in list_of_stuff:
			for e in sublist:
				newlist.append(e)
		return newlist
	
	def clefs_on_total_systems(list_of_clefs):
		single_list_of_staves = single_list(list_of_clefs)
		group_brackets = []
		print_clefs = []
		index=0
		while index < number_of_systems:
			j = 0
			while j < len(single_list_of_staves):
				clef = single_list_of_staves[j][1]
				page_offset = index*staff_spacing*amount_of_staves
				print_staff_y = (page_length - (top_bottom_margin))-((j)*staff_spacing+page_offset)
				position = left_right_margin, print_staff_y
				print_clefs.append(generate_clef(position, clef))
				j+=1
			index+=1
		index = 0
		while index < number_of_systems:
			group_brackets.append(draw_group_brackets(list_of_lists_of_clefs, x_offset, index))
			index+=1 
		return print_clefs,group_brackets
	
	print_clefs = clefs_on_total_systems(list_of_lists_of_clefs)[0]
	print_clefs = string.joinfields(print_clefs,'')
	group_brackets = clefs_on_total_systems(list_of_lists_of_clefs)[1]
	group_brackets = string.joinfields(single_list(group_brackets),'')
	#print print_clefs
	#print group_brackets
	return print_clefs+group_brackets#, staff_spacing, top_bottom_margin 
def clefs_on_pages(num_of_pages, list_of_lists_of_clefs):
	place_clefs = generate_clefs(list_of_lists_of_clefs,x_offset)#[0]
	place_clefs = string.joinfields(place_clefs,'')
	index = 0
	while index < num_of_pages:
		page_num = index + 1
		pages = open(path_file+str(page_num)+'.ps', 'a')
		pages.write(place_clefs)
		index += 1

		
def random_placed_notes(how_many, (start_time,end_time),(octave_up,octave_down),(clef)):
	index = 0
	list_of_values = []
	while index < how_many:
		a = random.randint(0,1)
		if a == 0:
			a = -1
		list_of_values.append([random.randint(start_time,end_time),(random.randint(0,23))/2.0, random.randint(octave_up,octave_down), a, 0,(clef,0)])
		index += 1
	list_of_values.sort(cmp)
	return list_of_values

def chromatic_run(x_factor,(low,high),clef):
	note_list = []
	i = 0
	while i < (high-low)*2:
		note_list.append([[[i*x_factor,(i+low)*.5,1,-1,0,(clef,0)]]])
		i += 1
	return note_list


def groups_and_note_entry((group_of_note_vals,last_note_time),(which_staff,of_how_many)):
	return multi_group_beamed_notes(group_of_note_vals,last_note_time,(which_staff,of_how_many))
	
#def independent_lists_of_beamed_notes(list_of_lists, staff_time):
#	split = split_groups(list_of_lists, staff_time)
	

#split large group into smaller groups based upon group_mem[0]/staff_size
	#for each element in list of beamed, send to beaming function
	#x_y extension is constant if e!=first element (=0)
	#^^^^^still kinda busted++++++WORKS!
#create 'staff spacing' variable.  no. of staves?  page size variable?+
#note->staff inside or outside note_function?+
#document.write for multipages+
#create stemming algo+
#create beaming algo+
#create beaming distance algo--function of lowest or highest note in group+
#beam extensions+
#do translate before beaming+
#calculate beaming across staves+
#minimum stemming length--distance from 'break point'+good
#fix end of staff beam & overspill+
#end note length in a group of beamed notes+
#end note length to carry over into next staff+
#create parenthetical ote wrap-around...close+
#24-tone system+
#add arrow at wrap around+--also, mid group wrap-arounds+
#create multi-system pages+clefs and transpositions+
#dynamics? grace-notes?
#---work on parsing of SDIF data---
#	1) first interpolate and create hard values for each x,partial 2) then create weighted partial preference rule 3) 'slice time' variable
	#-a multiple of amounts of x values 4) for slice and prefered partials -> amplitude = duration [next x val = previous time + duration]stop group at end of sound
#staff_list_2 = [[['clarinet',g_clef]],[['bass clarinet',bass_clef]],[['piano',g_clef],['piano',bass_clef]]]
#end time+
#create mid-group beaming spill-over++++
#mid-system clef changes...  will need to add a constant for (ALL) staves after clef is inserted (calculate x-space required, then add)...
#intelligent accidental choice
#consider a log function for amp.->time
#DYNAMICS, consider as a function of analysis data... 1 idea: function of duration but randomized within certain range 2.function of difference in partial freq.
#arpeggiation 'direction' options:  1) randomized 2) upward/downward--pitch 3)amplitude ascending/descending++
#duration of silence?  function of average amplitude?+  randomized/stochastic?  func. of 'drift'

amount_of_staves = preferences.amount_of_staves#count_staves_from_systems(preferences.instrumentation)

number_of_systems = num_of_staves/amount_of_staves#make sure amount of staves is multiple  of...


#num_of_pages = 23
#staff_nums = count_staves_from_systems(staff_list_2)
#staff_nums = 7


def groups_and_end_times(groups_and_end_times,(which_staff,staff_nums)):
	for e in groups_and_end_times:
		multi_group_beamed_notes(e[0],e[1],(which_staff,staff_nums))
def get_beam_and_note_data(note_data,(which_staff,how_many)):
	beam_and_note_data = []
	for e in note_data:
		note_group_data = beam_and_note_head_data(e[0],(which_staff,how_many))
		beam_and_note_data.append(note_group_data[0])
	return note_group_data, beam_and_note_data
