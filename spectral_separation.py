import sys, string, time, copy

if __name__ == '__main__':
	aiff_file = str(sys.argv[1])
	minimum_duration = float(sys.argv[2])
	minimum_amplitude = float(sys.argv[3])
	resampling_interval = float(sys.argv[4])
	if len(sys.argv) > 5:
		extra_args = string.join(sys.argv[5:])
	else:
		extra_args = ''
else:
	minimum_duration, minimum_amplitude, resampling_interval = .25,.05,.25
	aiff_file = '/Users/db/Desktop/music_xml/1_Hollywood_Vine_L_1_min_filter_n10.1.101..5.aif'
	extra_args = ''
	
#import _main

time_stamp = string.join(string.split(time.ctime()),'_')

from mxml import *
from auto_loris import *
from sdif_to_note import *
from partial_sorter import *
import general_functions
from orchestra import *
import putil

lf = Loris_set(aiff_file)

#lf.minimum_duration,lf.minimum_amplitude,lf.resampling_interval = .4, .49, .25
lf.analyze_if_needed(aiff_file).set_params(minimum_duration, minimum_amplitude, resampling_interval).thin().resample(resampling_interval)

partials_list = lf.make_list()

class Separation:
	def __init__(self, partials = None):
		self._partials = partials
	def starts_and_stops(self):
		starts_stops_n_averages = []
		for partial in self._partials:
			partial_number = partial[0][0]
			
			average_freq = general_functions.average_c(partial)
			average_amp = general_functions.average_d(partial)
			average_phase = general_functions.average_e(partial)
			
			start_end = [partial[0][1], partial[-1][1]]
			#############
			partial_entry = [partial_number, start_end, average_freq, average_amp, average_phase]
			#############
			starts_stops_n_averages.append(partial_entry)
		return starts_stops_n_averages

s=Separation(partials_list).starts_and_stops()

#for e in s:
#	print frequency_to_twelve_plus_cents(e[2])

s.sort(general_functions.bsort)
last_beat = s[-1][1][1]
last_measure = last_beat/4
o = Orchestra(full_orchestra)
o.stitch_measures([4,4],last_measure)

print last_beat, 'LAST BEAT!'

s.sort(general_functions.dsort)
max_amp = 100+general_functions.amplitude_to_dB(s[-1][3]+.0001)

print max_amp

s.sort(general_functions.bsort)

#print s
#s=[]
random.seed(10)

class a:
	def __init__(self):
		self._new = None
	def d(self, new = None):
		self._new = new or self._new
		return self
	

dynamic_constant = 4#has been 6 for a while...

def planks_from_spectrum(s):
	dynamic_group=[]
	for e in s:
		
		start, stop = e[1]
		pitch_48, pitch_24, pitch_12 = frequency_to_forty_eight(e[2]), frequency_to_twenty_four(e[2]), frequency_to_twelve(e[2])
		
		note_48, octave_48 = midi_to_note_and_oct(pitch_48)
		note_24, octave_24 = midi_to_note_and_oct(pitch_24)
		note_12, octave_12 = midi_to_note_and_oct(pitch_12)
		
		part = o.statistical_chooser(pitch_12, (start,stop))
		######
		amp = 100+general_functions.amplitude_to_dB(e[3]+.0001)
		
		dynamic = general_functions.clip(int(round(putil.fit(amp,0.0, max_amp,0,9)))-dynamic_constant,(0,9))
		dynamic_group.append(dynamic)

		######
		if part:
			part._partial_components.append(e)
			#print start,  'START', stop, 'STOP'
			p = Plank().position(start, stop).dynamic(Dynamic.dynamics[dynamic], part_for_adjustment = part)
			#if part._microtones == 'quarter':
			if part.microtonal_capability_in_range(pitch_48) == 'quarter':
				p.pitch(Note.descending_24_tone[int(note_24*2)]).octave(int(octave_24)).add_to_part(part)
			#elif part._microtones == 'all':
			elif part.microtonal_capability_in_range(pitch_48) == 'all':
				p.pitch(Note.descending_48_tone[int(note_48*4)]).octave(int(octave_48)).add_to_part(part)
			else:
				p.pitch(Note.pitches_flat[int(note_12)]).octave(int(octave_12)).add_to_part(part)
	#print dynamic_group
			
	

	file_name = general_functions.strip_file(aiff_file)
	
	#o_trans = copy.deepcopy(o)
	
	#o_trans.transpose_parts()
	
	#o_trans.output('/Users/db/Desktop/music_xml/Norchest__%s%.2f%.4f%.2f_%s_%s_TRANSPOSE.xml'%(file_name, minimum_duration, minimum_amplitude, resampling_interval, time_stamp, extra_args))
	#o_trans.floating_infos_output('/Users/db/Desktop/music_xml/Norchest__%s%.2f%.4f%.2f_%s_%s_TRANSPOSE_float_infos.txt'%(file_name, minimum_duration, minimum_amplitude, resampling_interval, time_stamp, extra_args))
#
	o.transpose_parts()
	o.output('/Users/db/Desktop/music_xml/Norchest__%s%.2f%.4f%.2f_%s_%s_.xml'%(file_name, minimum_duration, minimum_amplitude, resampling_interval, time_stamp, extra_args))
	o.floating_infos_output('/Users/db/Desktop/music_xml/Norchest__%s%.2f%.4f%.2f_%s_%s_float_infos.txt'%(file_name, minimum_duration, minimum_amplitude, resampling_interval, time_stamp, extra_args))
#
if __name__ == '__main__':	
	planks_from_spectrum(s)
	
#xxfix tag function...
#XXXremove redundant dynamics...
#XXXimplement 48-tone for:  strings-yes; winds-eh; others-nah
#look closer at 'orchestration'
#	used 'already played' as variable...
#	also, prefer choirs--strings
#'reversal' of tied pitches at the right points..
#--Change the order so that evens fall on evens, etc....
#
