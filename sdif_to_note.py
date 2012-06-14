#!usr/bin/python
import general_functions,random,math,putil,partial_sorter#,notes
g_clef = '\n(&) show'
#bass_clef = '\n(?) show'
#alto_clef = '\n(B) show'


#def midi_to_note_and_octave(midi_note,middle_c=60):
#	octave = int((midi_note-middle_c)/12)
#	note = 	midi_note%12
#	return [note, octave]
###########FIXED +4
#def midi_to_note_and_oct(midi_note,middle_c=60):
#	octave = int((midi_note-middle_c)/12)+4
#	note = 	midi_note%12
#	return [note, octave]
			
#def frequency_to_note_and_octave(frequency, twenty_four_or_twelve=0, base_a4=440,middle_c=60):
#	if twenty_four_or_twelve == 0:
#		return midi_to_note_and_octave(frequency_to_twenty_four(frequency,base_a4),middle_c)
#	elif twenty_four_or_twelve == 1:
#		return midi_to_note_and_octave(frequency_to_twelve(frequency,base_a4),middle_c)
def arpegiate(times,arpegiation_direction):
	if arpegiation_direction == 'ascending' or 1:#ascending arpeggiation
		times.sort(general_functions.csort)
	if arpegiation_direction == 'descending' or 0:#descending arp
		times.sort(general_functions.csort_reverse)
	if arpegiation_direction == 'amplitude' or 2:#this is amplitude sort
		times.sort(general_functions.dsort)
	if arpegiation_direction == 'reverse_amp' or 3:#reverse amp sort
		times.sort(general_functions.dsort_reverse)
	if arpegiation_direction == 'random' or 4:#random sort
		times.sort(general_functions.randsort)
	if arpegiation_direction == 'swap_one' or 5:#swap one permutation
		times = general_functions.swap_one_permute(times)
def groups_from_time_data(matrix,x_scale, clef = g_clef, low_oct = -1, high_oct = 2, transpose = 0, start_time = 0,pause_time = 1000., minimum_x_distance = 16, arpegiation_direction = 1):
	def yank_from_groups_to_group(groups,which_member):
		newgroup = []
		for e in groups:
			newgroup.append(e[which_member])
		return newgroup
	un_grouped_matrix = partial_sorter.remove_grouping(matrix)
	un_grouped_matrix.sort(general_functions.dsort)
	softest_amp = un_grouped_matrix[0][3]
	loudest_amp = un_grouped_matrix[-1][3]
	current_time_accum = start_time
	total_groups = []
	total_dynamics_group = []
	j = 0
	while j < len(matrix):#for times in matrix:
		times = matrix[j]
		if j < len(matrix)-1:
			next_times = matrix[j+1]
		else:
			next_times = matrix[0]
		arpegiate(times, arpegiation_direction)
		list_of_freqs = yank_from_groups_to_group(times,2)
		average_freqs = general_functions.average(list_of_freqs)
		next_freqs = yank_from_groups_to_group(next_times,2)
		next_average_freqs = general_functions.average(next_freqs)
		#---
		list_of_amps = yank_from_groups_to_group(times,3)
		
		average_amps = general_functions.average(list_of_amps)
		next_amps = yank_from_groups_to_group(next_times,3)
		next_average_amps = general_functions.average(next_amps)

		average_amps_ten = int(round(putil.fit(average_amps,softest_amp,loudest_amp,0.,10.))+1)
		average_phase = general_functions.average(yank_from_groups_to_group(times,4))
		average_phase_ten = int(round(putil.fit(average_phase,0.,6.2831853071795862,0.,10.)))
		#print average_phase_ten
		delta_freqs = average_freqs - next_average_freqs
		delta_amplitude = average_amps - next_average_amps
		abs_delta_amplitude = general_functions.clip(abs(delta_amplitude),(0.,1.))
		abs_delta_amplitude_ten = int(general_functions.clip(round(abs_delta_amplitude*3000),(0,9)))
		#print abs_delta_amplitude_ten
		#dynamics_group.append([(current_time_accum,-30),abs_delta_amplitude_ten])
		#print 0,average_amps_ten*2,average_phase_ten
		#print abs_delta_amplitude_ten,'delta',average_amps_ten,'average'
		dynamics_for_klang = general_functions.drunk_list((0,int(average_amps_ten)+random.randint(-1,2)),3,len(times)+1)
		print dynamics_for_klang
		#print dynamics_for_klang
		if abs_delta_amplitude != 0:
			inv_delta_amplitude = 1./(abs_delta_amplitude)
		else:
			inv_delta_amplitude = pause_time
		#print abs_delta_amplitude*1000000
		#print delta_freqs,'DELTA freqs', delta_amplitude,'Delta amplitude'
		#print next_average_freqs, 'next avg freqs', next_average_amps,'next avg amps'#, average_freqs,'AVERAGE FREQs',average_amps,'Average amps'
		#print dynamics_group
		chunk_element = []
		chunk_dynamics_group = []
		i = 0
		while i < len(times):#for partial in times:
			partial = times[i]
			time = partial[3]
			phase = putil.fit(partial[4],0.,6.2831853071795862,0.,1.)#float 0-1.
			phase_ten = int(round(phase*10))
			#amplitude_list_for_partial = yank_from_groups_to_group(partial,1)
			print phase
			partial_frequency = partial[2]
			#print current_time_accum
			pitch_midi = frequency_to_twenty_four(partial_frequency)+transpose
			pitch = midi_to_note_and_octave(pitch_midi)
			note = pitch[0]
			octave = general_functions.clip(pitch[1],(low_oct,high_oct))
			x_pos = current_time_accum
			#dynamic = [(x_pos,-20),phase_ten]
			#print dynamics_for_klang[i]
			chunk_dynamics_group.append([(int(round(x_pos)),-30),dynamics_for_klang[i]])
			values = [int(round(x_pos)),note,octave,-1, 0,(clef,0)]
			chunk_element.append(values)
			current_time_accum += (time*x_scale)+minimum_x_distance
			i+=1
		end_time = (times[-1][3]*x_scale)+minimum_x_distance
		number_of_group_members = len(chunk_dynamics_group)
		current_time_accum += general_functions.clip(((abs_delta_amplitude*10000000)*(1./number_of_group_members)),(0,notes.staff_time*1.))+end_time
		total_dynamics_group.append(chunk_dynamics_group)
		total_groups.append([chunk_element]+[int(round(end_time))])
		j += 1
	return total_groups,total_dynamics_group#includes the end time as e[1] of note group
	
def groups_from_time_data(matrix,x_scale, clef = g_clef, low_oct = -1, high_oct = 2, 
	transpose = 0, start_time = 0,pause_time = 1000., minimum_x_distance = 16, 
	arpegiation_direction = 1, group_silence_factor = 10000000, tuning = 'cents',
	note_head = 'normal'):
	def yank_from_groups_to_group(groups,which_member):
		newgroup = []
		for e in groups:
			newgroup.append(e[which_member])
		return newgroup
	
	#matrix.reverse()#reverses entire piece!!!	
	un_grouped_matrix = partial_sorter.remove_grouping(matrix)
	un_grouped_matrix.sort(general_functions.dsort)
	softest_amp = un_grouped_matrix[0][3]
	loudest_amp = un_grouped_matrix[-1][3]
	current_time_accum = start_time
	articulations = []
	total_groups = []
	total_dynamics_group = []
	cents_group = []
	j = 0
	while j < len(matrix):#for times in matrix:
		times = matrix[j]
		if j < len(matrix)-1:
			next_times = matrix[j+1]
		else:
			next_times = matrix[0]
		arpegiate(times, arpegiation_direction)
		list_of_freqs = yank_from_groups_to_group(times,2)
		average_freqs = general_functions.average(list_of_freqs)
		next_freqs = yank_from_groups_to_group(next_times,2)
		next_average_freqs = general_functions.average(next_freqs)
		#---
		list_of_amps = yank_from_groups_to_group(times,3)
		
		average_amps = general_functions.average(list_of_amps)
		next_amps = yank_from_groups_to_group(next_times,3)
		next_average_amps = general_functions.average(next_amps)
		#--
		list_of_phases = yank_from_groups_to_group(times,4)
		largest_phase = putil.fit(max(list_of_phases),0.,6.2831853071795862,0.,1.)
		smallest_phase = putil.fit(min(list_of_phases),0.,6.2831853071795862,0.,1.)
		average_amps_ten = int(round(putil.fit(average_amps,softest_amp,loudest_amp,0.,9.))+1)
		average_amps_one = putil.fit(average_amps,softest_amp,loudest_amp,0.,1.)
		average_phase = general_functions.average(list_of_phases)
		average_phase_ten = int(round(putil.fit(average_phase,0.,6.2831853071795862,0.,9.)))
		average_phase_one = putil.fit(average_phase,0.,6.2831853071795862,0.,1.)
		#print average_phase_one
		delta_freqs = average_freqs - next_average_freqs
		delta_amplitude = average_amps - next_average_amps
		abs_delta_amplitude = general_functions.clip(abs(delta_amplitude),(0.,1.))
		abs_delta_amplitude_ten = int(general_functions.clip(round(abs_delta_amplitude*3000),(0,9)))
		dynamics_for_klang = general_functions.drunk_list((0,int(average_amps_ten)+random.randint(-1,2)),3,len(times)+1)
		articulation = general_functions.clip((1-(average_phase_one*1.5)),(0.,1))
		articulations.append([current_time_accum,articulation])
		if abs_delta_amplitude != 0:
			inv_delta_amplitude = 1./(abs_delta_amplitude)
		else:
			inv_delta_amplitude = pause_time
		chunk_element = []
		chunk_dynamics_group = []
		i = 0
		#print 'NOTE HEAD '+note_head
		while i < len(times):#for partial in times:
			partial = times[i]
			time = partial[3]
			phase = putil.fit(partial[4],0.,6.2831853071795862,0.,1.)#float 0-1.
			#print phase
			phase_ten = int(round(phase*10))
			partial_frequency = partial[2]
			if tuning == 'cents':
				pitch_midi = partial_sorter.frequency_to_twelve_plus_cents(partial_frequency)[0]+transpose
				cents_deviation = partial_sorter.frequency_to_twelve_plus_cents(partial_frequency)[1]
			if tuning == 'quarter':
				pitch_midi = frequency_to_twenty_four(partial_frequency)+transpose
				cents_deviation = ''
			elif tuning == 'semi':
				pitch_midi = frequency_to_twelve(partial_frequency)+transpose
				cents_deviation = ''
			#print note_head
			#note_head = 'random'
			if note_head == 'random':
				head = str((random.randint(1,5)))#str(int(round(putil.fit(phase_ten,0,10,1,9))))#
			else:
				head = note_head
			pitch = midi_to_note_and_octave(pitch_midi)
			note = pitch[0]
			octave = general_functions.clip(pitch[1],(low_oct,high_oct))
			x_pos = current_time_accum
			#print head
			chunk_dynamics_group.append([(int(round(x_pos)),-30),dynamics_for_klang[i]])
			values = [int(round(x_pos)),note,octave,-1, head,(clef,0)]#int(round(x_pos))
			chunk_element.append(values)
			cents_group.append([(x_pos,35),cents_deviation])
			current_time_accum += (time*x_scale)+minimum_x_distance
			i+=1
		end_time = (times[-1][3]*x_scale)+minimum_x_distance
		number_of_group_members = len(chunk_dynamics_group)
		current_time_accum += general_functions.clip(((abs_delta_amplitude*group_silence_factor)*(1./number_of_group_members)),(0,notes.staff_time*1.))+end_time
		total_dynamics_group.append(chunk_dynamics_group)
		total_groups.append([chunk_element]+[int(round(end_time))])
		j += 1
	#print articulations
	return total_groups,total_dynamics_group,articulations,cents_group#includes the end time as e[1] of note group
