import general_functions, string, math

xml_header ="""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE score-partwise PUBLIC "-//Recordare//DTD MusicXML 1.0 Partwise//EN"
                                "http://www.musicxml.org/dtds/partwise.dtd">\n<!--by G.Douglas Barrett-->\n"""

def num_tabs(n):
	return '  '*n

#def insert_tabs_on_returns(s, num_of_tabs):
#	new=''
#	for e in s:
#		new+=e
#		if e == '\n':
#			new+=num_tabs(num_of_tabs)
#	del s
#	return new
	
def insert_tabs_on_returns(s, num_of_tabs):
	new=''
	orig=s.splitlines()
	new+=orig[0]
	i=1
	while i < len(orig):
		new+= '\n'+num_tabs(num_of_tabs)+orig[i]
		i+=1
	return new
def tagify(tag_name_1, s, indent=0, tag_name_2 = None):
	tag_name_2 = tag_name_2 or tag_name_1
	indention = num_tabs(indent)
	string = insert_tabs_on_returns(s, indent+1)
	return '%s<%s>\n%s  %s\n%s</%s>' % (indention, tag_name_1,indention, string, indention, tag_name_2)
def tag_single(tag_name_1,s,tag_name_2 = None):
	tag_name_2 = tag_name_2 or tag_name_1
	return '<%s>%s</%s>'%(tag_name_1, s, tag_name_2)
def tag_self(tag_name):
	return '<%s/>' % tag_name
def check_index(member, list):
	i=0
	for e in list:
		if e == member:
			return i
			break
		i+=1
	return None
n='\n'

treble_clef = ['G',2]
alto_clef = ['C',3]
bass_clef = ['F',4]

def frequency_to_twenty_four(frequency,base_a4=440):
	return round((12*math.log((float(frequency)/base_a4),2)+69.)*2.)*.5

def frequency_to_forty_eight(frequency,base_a4=440):
	return round((12*math.log((float(frequency)/base_a4),2)+69.)*4.)*.25

def frequency_to_twelve(frequency,base_a4=440):
	return round((12*math.log((float(frequency)/base_a4),2)+69.))


def note_and_octave_to_midi((note,octave)):
	if note in Note.pitches_sharp:
		number = general_functions.check_index(note, Note.pitches_sharp)
	elif note in Note.pitches_flat:
		number = general_functions.check_index(note, Note.pitches_flat)
	elif note in Note.ascending_48_tone:
		number = general_functions.check_index(note, Note.ascending_48_tone)/4.0
	elif note in Note.descending_48_tone:
		number = general_functions.check_index(note, Note.descending_48_tone)/4.0
	midi =  12 + octave*12 + number
	return midi
	
def midi_to_note_and_oct(midi_note,middle_c=60):
	octave = int((midi_note-middle_c)/12)+4
	note = 	midi_note%12
	return [note, octave]
	
def transpose((note, octave), amount):
	midi = note_and_octave_to_midi([note,octave])
	transposed = midi + amount
	note_trans, oct_trans = midi_to_note_and_oct(transposed)
	if note in Note.descending_48_tone:
		transposed_pitch = Note.descending_48_tone[int(note_trans*4)]
	else:
		transposed_pitch = Note.ascending_48_tone[int(note_trans*4)]
	return transposed_pitch, oct_trans
	

def calculate_staff_position((pitch, octave), clef):
	if clef[0] == 'b':###WTF!?
		clef = ['F',4]
	f_five_midi = 77
	f_five_positions = {'G':77,'C':67,'F':57}#the midi note names of the top line of each clef
	midi_pitch = note_and_octave_to_midi((pitch, octave))
	return int((round(((f_five_positions[clef[0]] - midi_pitch)/4.0))*12)*-1)
	
class Score:
	
	instruments = []
	
	def __init__(self, file_name='default.xml'):
		self.header = ''
		self.parts_header = ''
		self.file_name=file_name
	def read_instrumentation(self):
		print_instrument_headers = ''
		for part in Score.instruments:
			print_instrument_headers+=part.header_data()
		return print_instrument_headers
	def print_header(self):
		#return tagify('part-list', self.read_instrumentation(),0)
		return tagify('part-list', self.read_instrumentation(),1)#MOVE BACk to 0 for OLD Method!!!
	def print_parts(self):
		parts_text = ''
		for part in Score.instruments:
			parts_text+=part.print_part()
		print '(parts done)'
		return parts_text
	def print_score(self):
		#return xml_header+tagify('score-partwise',self.print_header()+n+self.print_parts(),0)
		return xml_header+'\n'+'<score-partwise>'+'\n'+self.print_header()+'\n'+self.print_parts()+'</score-partwise>'
	def transpose_parts(self):
		for part in Score.instruments:
			part.transpose()
		return self
	def output(self, file_name = None):
		file_name=file_name or self.file_name
		fp = open(file_name, 'w')
		fp.write(self.print_score())
		fp.close()
		print 'Wrote Music XML file at %s' % file_name
	def floating_infos_output(self, file_name = None):
		file_name=file_name or self.file_name[:-4]+'_float_infos.txt'
		fp = open(file_name, 'w')
		float_infos = ''
		for part in Score.instruments:
			float_infos+=part.return_floating_infos()
		fp.write(float_infos)
		fp.close()
		print 'Wrote Floating Infos file at %s' % file_name
class Part:
	serial_number=0
	def add(self):
		if self not in Score.instruments:
			Score.instruments.append(self)
	def remove(self):
		position_in_instruments = check_index(self,Score.instruments)
		if position_in_instruments != None:
			del Score.instruments[position_in_instruments]
	def __init__(self):
		Part.serial_number += 1
		self.number = Part.serial_number
		self._name = ''
		self._abbreviation = ''
		self.staves = 1
		self.midi_channel = Part.serial_number
		self._program = 1
		self.measures = []
		self._measure_numbers = []
		self._starting_measure_number = 1
		self._floating_notes = []
		self._planks = []
		self._clef = treble_clef
		self._group, self._group_name, self._group_abbrev, self._bracket, self._group_barline, self._bracket = None, None, None, None, 'yes','yes'
	
		self._floating_infos = []
		
		self.add()
	def name(self, name = None, abbreviation = None):
		if name:
			self._name = name
		if abbreviation:
			self._abbreviation = abbreviation
		return self
	
	def sort_planks(self):
		self._planks.sort(general_functions.index_sort)
		return self
		
	def floating_infos(self):
		self._floating_infos = []#problem not ordering floaters???!!
		#for plank in self._floating_notes:#
		#	if plank.__class__ == Plank:
		#		self._floating_infos.append([[plank._part_position, plank._end_position], [plank._pitch, plank._octave], plank._dynamic])
		for plank in self.sort_planks()._planks:
			self._floating_infos.append([[plank._part_position, plank._end_position], [plank._pitch, plank._octave], plank._dynamic])
		return self
	def return_floating_infos(self):
		floating_infos_text = '\n\n----Floating notes for %s part (%s)----\n\n'%(self._name, self._abbreviation)
		for plank in self.floating_infos()._floating_infos:
			start, end = plank[0][0],plank[0][1]
			measure_start, beat_start = int(start/4)+1, start%4#$#####################FFFFFFFUUucKed for the moment -- works only if all's in 4/4
			measure_end, beat_end = int(end/4)+1, end%4
			floating_infos_text+='%.2f,%f absolute --- measure start %d beat start %f  --- measure end %d beat end %f -- pitch at %s octave at %d -- dynamic at %s\n'%(plank[0][0],plank[0][1],measure_start, beat_start, 
			measure_end, beat_end, plank[1][0],plank[1][1],plank[2]._symbol)
		return floating_infos_text
	def auto_accidentalize(self):
		def sharp_candidate(tone_a, tone_b):
			def strip_eighth(tone):
				if tone[-1] in ['^','_']:
					return tone[:-1], tone[-1]
				else:
					return tone, ''
				
			tone_a_stripped, tone_a_remainder = strip_eighth(tone_a)
			
			tone_b_stripped, tone_b_remainder = strip_eighth(tone_b)
			
			index_a = check_index(tone_a_stripped,Note().pitches_flat)
			index_b = check_index(tone_b_stripped,Note().pitches_flat)
			
			#FIX:  POTENTIAL AUGMENTED 2NDS, weird spellings, etc. Ab - D#
			#if [index_a, index_b] in [[1,2],[3,4],[6,7],[8,9],[10,11]] or [index_a, index_b] in  [[1,4],[6,9],[8,11]] or [index_a, index_b] in [[11,1],[4,6]] or [index_a, index_b] in [[11,6]]:
			if [tone_a_stripped, tone_b_stripped] in [['Db','D'],['Eb','E'],['Gb','G'],['Ab','A'],['Bb','B']] or [tone_a_stripped, tone_b_stripped] in  [['Db','E'],['Gb','A'],['Ab','B'], ['E','Db'],['A','Gb'],['B','Ab']] or [tone_a_stripped, tone_b_stripped] in [['B','Db'],['E','Gb']] or [tone_a_stripped, tone_b_stripped] in [['B','Gb'], ['Gb','B']]:
				return Note().pitches_sharp[index_a]+tone_a_remainder, Note().pitches_sharp[index_b]+tone_a_remainder
			
			else:
				return tone_a, tone_b
		#3-ORDER ACCIDENTAL CORRECTION##################
		#i = 1
		#while i < len(self._planks)-1:
		#	current_plank_pitch = self._planks[i]._pitch
		#	next_plank_pitch = self._planks[i+1]._pitch
		#	previous_plank_pitch = self._planks[i-1]._pitch
		#	
		#	previous_and_current_pitches = sharp_candidate(previous_plank_pitch, current_plank_pitch)
		#	previous_and_next_pitches = sharp_candidate(previous_plank_pitch, next_plank_pitch)
		#	
		#	self._planks[i-1]._pitch = previous_and_current_pitches[0]
		#	self._planks[i]._pitch = previous_and_current_pitches[1]
		#	self._planks[i+1] = previous_and_next_pitches[1]
		#	
		#	i+=1
			
		##################
		#4-ORDER ACCIDENTAL CORRECTION##################
		i = 0
		while i < len(self._planks)-3:
			plank_pitch_A = self._planks[i]._pitch
			plank_pitch_B = self._planks[i+1]._pitch
			plank_pitch_C = self._planks[i+2]._pitch
			plank_pitch_D = self._planks[i+3]._pitch
			
			pitches_A_B = sharp_candidate(plank_pitch_A, plank_pitch_B)
			pitches_A_C = sharp_candidate(plank_pitch_A, plank_pitch_C)
			pitches_A_D = sharp_candidate(plank_pitch_A, plank_pitch_D)
			
			self._planks[i]._pitch = pitches_A_B[0]
			self._planks[i+1]._pitch = pitches_A_B[1]
			self._planks[i+2]._pitch = pitches_A_C[1]
			self._planks[i+3]._pitch = pitches_A_D[1]
			
			i+=1
			
		return self
	#############
	def transpose(self, transposition = None):
		#print self._clef, self._transposed_clef, 'CLEF TRANSPOSITION'
		transposition = transposition or self._transposition
		self._clef = self._transposed_clef################################Potential CLEF PROBLEM?
		for plank in self._planks:
			#print transposition, 'TRANSPOSITION'
			plank.transpose(transposition)
		return self
	#############
	def group(self, start_or_stop = None, group_name = None, group_abbrev = None, barline = 'yes', bracket = 'yes'):
		if start_or_stop:
			self._group = start_or_stop
		if group_name:
			self._group_name = group_name
		self._group_barline = barline
		self._bracket = bracket
		return self
	def starting_measure_number(self, number):
		self._starting_measure_number = number
		return self
	def order_measures(self):
		self.measures.sort(general_functions.index_sort)
		return self
	def clef(self, clef):
		self._clef = clef
		return self
	def measure_numbers(self):
		self._measure_numbers = []
		for measure in self.order_measures().measures:
			self._measure_numbers.append(measure._measure_number)
		return self
	def measures_info(self):
		self._measure_infos = {}
		for measure in self.order_measures().measures:
			self._measure_infos[measure._measure_number] = measure._total_vals#add other info
		return self
	def insert_measure(self, number, insert_overwrite = 'insert'):
		self.measure_numbers()
		if number in self.measure_numbers()._measure_numbers:
			if insert_overwrite == 'insert':
				for measure in self.measures:
					if measure._measure_number >= number:
						measure.number(number+1)
			if insert_overwrite == 'overwrite':
				i = 0
				while i < len(self.measures):
					if self.measures[i]._measure_number == number:
						del self.measures[i]
					i+=1
		return Measure(self).number(number)#self <--- RETURNS COPY OF MEASURE!!!!!!
	def overwrite_measure(self, number):
		return self.insert_measure(number, 'overwrite')#<--- RETURNS COPY OF MEASURE!!!!!!
	def check_for_contiguous_measures(self):
		self.order_measures()
		i = 2
		while i < len(self.measures):
			if self.measures[i]._measure_number != self.measures[i-1]._measure_number + 1:
				#print i, i-1
				raise ValueError('not all measures currently present %d not consec' % i)
			i+=1
		return True
	def attach_floating_note(self, note):
			i = 0
			current_value = 0
			while i < len(self.measures):
				
				#self.measures is LIST self._measure_infos is DICT!!!!
				if note._part_position >= current_value and note._part_position < current_value + self._measure_infos[i+1]:
					note.add_to_measure(self.measures[i]).position(measure_position = note._part_position - current_value)
				current_value += self._measure_infos[i+1]
				i+=1
				
	def attach_floating_notes(self):
		if self.check_for_contiguous_measures():#possible to just check for proposed measure???
			for note in self.order_measures().measures_info()._floating_notes:
				if note.__class__ == Note:
					self.attach_floating_note(note)
				#if note.__class__ == Plank:
					#print 'Plank found, biatch'
		return self
	
	def remove_redundant_dynamics(self):
		if self.check_for_contiguous_measures() and len(self._planks) > 0:#possible to just check for proposed measure???
			new_thing = ''
			i = 1
			while i < len(self.order_measures().sort_planks().measures_info()._planks):
				if self._planks[i]._dynamic._symbol != new_thing:
					new_thing = self._planks[i]._dynamic._symbol
					
				if self._planks[i-1]._dynamic._symbol != new_thing:
					self._planks[i]._dynamic._show = 'yes'
				else:
					self._planks[i]._dynamic.hide()
				i+=1
			self._planks[0]._dynamic._show = 'yes'
			#i = 1
			#while i < len(self.order_measures().sort_planks().measures_info()._planks):#!!!!add order Planks method!
				#if plank.__class__ == Plank:
			#	current_dynamic = self._planks[i]._dynamic
			#	previous_dynamic = self._planks[i-1]._dynamic
			#	current_dynamic.hide()
			#	if current_dynamic._symbol != previous_dynamic._symbol:# and previous_dynamic._show == 'yes':
			#		current_dynamic._show = 'yes'
			#	i+=1
			#if len(self._planks) > 0:
			#	self._planks[0]._dynamic._show = 'yes'
		return self
	def chop_planks(self):
		for plank in self._planks:
			plank.chop(self)
		return self
	def stitch_missing_measures(self, time_sig = [4,4], last_measure = None):
		if not last_measure:
			last_measure = self.order_measures().measures[-1]._index
		else:
			last_measure = last_measure+1
		measure_numbers = self.measure_numbers()._measure_numbers
		i = 1
		while i < last_measure:
			if i not in measure_numbers:
				Measure(self).number(i).time_sig(time_sig[0],time_sig[1])
			i += 1
		self.order_measures()
		return self
	def cover_empty_space_with_rests(self):
		print '--------Filling measures %s to %s with rests----------' % (self.measures[0]._measure_number, self.measures[-1]._measure_number)
		for measure in self.measures:
			measure.insert_rests()
		return self
	def header_data(self):
		if self._group == 'start':
			#name#####################Name
			if self._group_name:
				group_name= tag_single('group-name',self._group_name)+'\n'
			else:
				group_name = ''
			if self._group_abbrev:
				group_abbrev = tag_single('group-abbreviation',self._group_abbrev)+'\n'
			else:
				group_abbrev = ''
			#bracket#######################
			if self._bracket:
				bracket = tag_single('group-symbol','bracket')+'\n'
			else:
				bracket = ''
			if self._group_barline == 'yes':
				barline = tag_single('group-barline','yes')
			else:
				barline = ''
			group_start = tagify('part-group number="1" type="start"',group_name+group_abbrev+bracket+barline,0,'part-group')+'\n'
			group_end = ''
		elif self._group == 'stop':
			group_start = ''
			group_end = tag_self('part-group number="1" type="stop"')+'\n'
		else:
			group_start = ''
			group_end = ''
		num = str(self.number)
		midi_num = num
		part_id = 'score-part id=\"P'+num+'\"'
		part_name = tag_single('part-name',self._name)+'\n'
		part_abbreviation = tag_single('part-abbreviation',self._abbreviation)+'\n'
		instrument_name = tag_single('instrument-name', self._name)
		score_instrument_id = tagify('score-instrument id=\"P'+num+'-I'+num+'\"',instrument_name,0,'score-instrument')+'\n'
		midi_id = 'midi-instrument id=\"P'+midi_num+'-I'+midi_num+'\"'
		midi_channel = tag_single('midi-channel',midi_num)
		midi_program = tag_single('midi-program','1')#only piano for now--do a look-up table for all std. instruments
		midi = tagify(midi_id, midi_channel+'\n'+midi_program, 0, 'midi-instrument')
		return group_start+tagify(part_id,part_name+part_abbreviation+score_instrument_id+midi,0,'score-part')+'\n'+group_end
	def print_part(self):
		part_id = 'part id=\"P'+str(self.number)+'\"'
		part_text=''
		self.order_measures().measures[0].clef(self._clef)
		i=0####################################################
		for meausure in self.remove_redundant_dynamics().auto_accidentalize().chop_planks().attach_floating_notes().cover_empty_space_with_rests().measures:#<-------TAKES CARE Of Floats and Rests!!!!!!!1
			part_text+=self.measures[i].print_measure()+'\n'
			i+=1
		print 'Wrote measures for %s part'%self._name
		return tagify(part_id, part_text,1,'part')+'\n'##########--'1'adds an indent--#remove '\n'##<----change to tagify(part_id, part_text,0,'part') and use old score print method for slower part printing

class Note_group:
	
	"""A group of notes.  Contains notes or other groups of notes.
	Has a starting and ending measure.  Can be a beamed group or a tuplet"""
	
	def print_beams(self):
		if len(self.members) > 1:
			self.members[0].beam_status,self.members[-1].beam_status  = 'begin', 'end'
		if len(self.members)> 2:
			for note in self.members[1:-1]:
				note.beam_status = 'continue'
	def __init__(self, begin_measure, note_group = None, end_measure = None):
		self.begin_measure = begin_measure
		end_measure = end_measure or begin_measure
		self.members = []
		self.beams = 1
		if note_group:
			note_group.members.append(self)
			if len(self.members) > 1:
				self.print_beams()

		
class Rhythm:
	rhythms = [.03125,.0625,.125,.25,.5,1,2,4,8], ['128th','64th','32nd','16th','eighth','quarter','half','whole','breve']
	
	rhythm_dict={0.03125: '128th', 0.0625: '64th', 2:
	'half', 4: 'whole',8: 'breve', 0.5: 'eighth', 1: 'quarter', 0.25: '16th', 0.125: '32nd'}
	rhythm_vals={'128th': 0.03125, '32nd': 0.125, '64th': 0.0625, 'half': 
		2, 'quarter': 1, 'whole': 4, 'breve': 8, '16th': 0.25, 'eighth': 0.5, 'grace':0}
	
	spell_as_time_sig = {'128th':128,'64th':64,'32nd':32,'16th':16,'eighth':8,'quarter':4,'half':2,'whole':1}
	spell_as_beat = {128:'128th',64:'64th',32:'32nd',16:'16th',8:'eighth',4:'quarter',2:'half',1:'whole'}
	
	
	def tuplets(self, tuplet = 2):#, val, tuplet):
		self._value = Rhythm.rhythm_vals[self._type]
		self._value =  self._value*closest_2(tuplet)#self.rhythm_vals[self._type]*closest_2(tuplet)
		self._duration = self._value#*120
		return self
	#value = tuplets
	def dot(self):#, dots = None):
		self._dots+=1
		if self._dots == 1:
			self._old_val = self._value*.5
			self._value = self._value + self._old_val
		elif self._dots > 1:
			self._old_val = self._old_val*.5
			self._value += self._old_val
		self._duration = self._value#*120
		return self
	
	def value(self):
		return self

def is_whole_num(number):
	if int(number) == number:
		return True
	else:
		return False


class Note_group_(Rhythm):
	
	def __init__(self):
		self._beats = 4
		self._beat_type = 4
		self._beat_val = 1
		self._total_vals = self._beats*self._beat_val
		self._tuplet = 0
		#self._members = [None]*self._beats
	def count_beats(self):
		notes, rests, beats = 0,0,0
		for single_note in self.notes:
			#rhythmic_value=single_note.rhythm_vals[single_note._type]
			if single_note.__class__== Note:
				notes+=single_note.value()._value
			if single_note.__class__== Rest:
				rests+=single_note.value()._value
		self._current_beats = (notes+rests)#*float(self._beat_val)
		self._total_vals = self._beats*self._beat_val
		self._rests = rests
		self._notes = notes
		return self# {'notes':notes, 'rests':rests, 'beats':beats}
	def member(self, member, index = None):#########################################DESTROY ME
		index = index or len(self._members)#next in order (in other words)
		general_functions.insert(member,index-1, self._members)
		return self
	
	def empty_beats(self, beats = None):
		beats = beats or self._beats
		self.member(None, beats)
		return self
	def value_to_list(self, val, forwards_or_backwards = 'forwards'):
		list = []
		def nearest(val):
			i = len(Rhythm.rhythms[0])-1
			nearest = None
			while i >= 0:
				if val == Rhythm.rhythms[0][i]:
					nearest = Rhythm.rhythms[0][i]
				if val < Rhythm.rhythms[0][i] and val > Rhythm.rhythms[0][i-1]:
					nearest = Rhythm.rhythms[0][i-1]
				i-=1
			return nearest
		total = 0
		top_val = val
		while total < top_val:#reduce(lambda x, y: x+y,list)
			new_test = nearest(val)
			if type(new_test) in (float, int):
				list.append(new_test)
				val = val - new_test
				total += new_test
			else:
				break
		if forwards_or_backwards == 'forwards':
			list.reverse()
		return list
	def order_notes(self):
		self.notes.sort(general_functions.index_sort)
		for note in self.notes:
			note.position()
		#for note in self.notes:###################
		#	if note.__class__ == Note:
		#		if note.upper_chord_member == 'no':####
		#			self.notes.remove(note)###
		#			self.notes.insert(0,note)#
		return self
	def rests_for_list(self, list_of_rest_vals, start = 0):
		place_holder = 0
		for e in list_of_rest_vals:
			Rest(self).type(Rhythm.rhythm_dict[e]).position(start + place_holder)
			place_holder += e
	def notes_for_list(self, list_of_note_vals, params = ['C',1], part = None, start = 0, ties = 'yes', end_tie = 'no', 
	redundant_accidentals = 'hide', dynamic = None, articulations = None, dynamic_y_pos = None, dyn_show = None):
		place_holder = 0
		i = 0
		while i < len(list_of_note_vals):
			new_note = Note().type(Rhythm.rhythm_dict[list_of_note_vals[i]]).pitch(params[0]).octave(params[1]).add_to_part(part).position(part_position = start + place_holder)
			if ties == 'yes' and i != (len(list_of_note_vals)-1):
				new_note.tie()
			elif end_tie == 'yes':
				new_note.tie()
			if i == 0 and dynamic:
				new_note.dynamic(dynamic, y_position = dynamic_y_pos, show_hide = dyn_show)
			if i == 0 and articulations:
				new_note.articulations(articulations)
			if redundant_accidentals == 'hide' and i != 0:
				new_note.accidental('hide')
			place_holder += list_of_note_vals[i]
			i+=1
		return self
	def notes_for_value(self, value, params = ['C',1], direction = 'backwards', part = None, start = 0, ties = 'yes', end_tie = 'no', 
	redundant_accidentals = 'hide', dynamic = None, articulations = None, dynamic_y_pos = None, dyn_show = None):
		if is_whole_num(start):########CHEEP FIX ---  Watch out!!!
			direction = 'backwards'########CHEEP FIX ---  Watch out!!!
		else:				########CHEEP FIX ---  Watch out!!!
			direction = 'forwards'########CHEEP FIX ---  Watch out!!!
		self.notes_for_list(self.value_to_list(value, direction), params, part, start, ties, end_tie, 
		redundant_accidentals, dynamic, articulations, dynamic_y_pos, dyn_show)
		return self
		
	def notes_for_list_B(self, list_of_note_vals, params = ['C',1], part = None, start = 0, ties = 'yes', end_tie = 'no', 
	redundant_accidentals = 'hide', dynamic = None, articulations = None):
		place_holder = 0
		i = 0
		while i < len(list_of_note_vals):
			new_note = Note().type(Rhythm.rhythm_dict[list_of_note_vals[i]]).pitch(params[0]).octave(params[1]).add_to_part(part).position(part_position = start + place_holder)
			if ties == 'yes' and i != (len(list_of_note_vals)-1):
				new_note.tie()
			elif end_tie == 'yes':
				new_note.tie()
			if i == 0 and dynamic:
				new_note._dynamic = dynamic
			if i == 0 and articulations:
				new_note.articulations(articulations)
			if redundant_accidentals == 'hide' and i != 0:
				new_note.accidental('hide')
			place_holder += list_of_note_vals[i]
			i+=1
		return self
		
	def notes_for_value_B(self, value, params = ['C',1], direction = 'backwards', part = None, start = 0, ties = 'yes', end_tie = 'no', 
	redundant_accidentals = 'hide', dynamic = None, articulations = None):
		if is_whole_num(start):########CHEEP FIX ---  Watch out!!!
			direction = 'backwards'########CHEEP FIX ---  Watch out!!!
		else:				########CHEEP FIX ---  Watch out!!!
			direction = 'forwards'########CHEEP FIX ---  Watch out!!!
		self.notes_for_list_B(self.value_to_list(value, direction), params, part, start, ties, end_tie, 
		redundant_accidentals, dynamic, articulations)
		return self
	def fill_rests(self):#older 'ordered entry' rest filler
		remaining_beats = self.count_beats()._total_vals - self.count_beats()._current_beats
		for e in self.value_to_list(remaining_beats):
			Rest(self).type(Rhythm.rhythm_dict[e])
		self.count_beats()
		return self#remaining_beats
	
	def insert_rests(self):
		remaining_beats = self.count_beats()._total_vals - self._current_beats
		#print 'REMAINING BEATS', remaining_beats, self._current_beats, self.notes
		self.order_notes()
		#redo completely:
		
		if remaining_beats > 0:
			if len(self.notes) > 0:
				note_list = []
				if self.notes[0]._measure_position > 0:
					prepended_rests = self.notes[0]._measure_position
					note_list.append([0, prepended_rests])
				i = 0
				while i < len(self.notes)-1:
					space = self.notes[i+1]._measure_position - self.notes[i]._end_position
					if space > 0:
						note_list.append([self.notes[i]._end_position, space])
					i+=1
				if self.notes[-1]._end_position < self._total_vals:
					note_list.append([self._total_vals, self._total_vals - self.notes[-1]._end_position])
				#print note_list
				for time in note_list:
					self.rests_for_list(self.value_to_list(time[1]), start = time[0])
				
		self.order_notes()		
		return self
		
#NG = Note_group



class Tuplet(Note_group_):
	pass		
def time_sig_to_beat(val):
	return Rhythm.spell_as_time_sig[Rhythm.rhythm_dict[val]]
def beat_to_time_sig(beat):
	return Rhythm.rhythm_vals[Rhythm.spell_as_beat[beat]]
class Measure(Rhythm, Note_group_):
	
	def __init__(self,part):
		self.id = part.serial_number		
		self._measure_number = 1
		self.divisions = 4
		self.key = 0
		
		self._symbol = 'common'
		self._beats = 4
		self._beat_type = 4
		self._beat_val = 1
		self._total_vals = self._beats*self._beat_val
		
		self._time_sig = [self._symbol, self._beats, self._beat_type]
		self.staves = part.staves
		self._clef = None#['G', 2]
		self.part=part
		if self not in part.measures:
			part.measures.append(self)
		self._members = [None]*self._beats
		self.notes = []
		self.note_groups = []
		#self.empty_beats(self._beats)
	def number(self, number):
		self._index = number
		self._measure_number = number
		return self
	def beats(self, beats = None, beat_type = None):
		self._beats = beats or self._beats
		self._beat_type = beat_type or self._beat_type
		if (self._beats, self._beat_type) == (4,4):#4/4
			self._symbol = 'common'
		else:
			self._symbol = None
		self._time_sig = [self._symbol, self._beats, self._beat_type]
		self._beat_val = beat_to_time_sig(self._beat_type)
		self._members = [None]*self._beats
		self._total_vals = self._beats*self._beat_val
		return self
	time_sig = beats
	def clef(self, clef = None):
		self._clef = clef or self._clef
		return self
	def print_attributes(self):
		self.beats()
		divisions = tag_single('divisions',str(self.divisions))
		key = tagify('key',tag_single('fifths','0')+'\n'+tag_single('mode','major'),0)
		if not self._symbol:
			time_tag = ''
		else:
			time_tag = ' symbol=\"'+ self._symbol+ '\"'
		time = tagify('time'+time_tag, tag_single('beats',str(self._time_sig[1]))+'\n'+tag_single('beat-type',str(self._time_sig[2])),0,'time')
		if self._clef:
			clef = tagify('clef', tag_single('sign',self._clef[0])+'\n'+tag_single('line', self._clef[1]),0)
		else:
			clef = ''
		return tagify('attributes',divisions + n + key + n + time + n + clef,0)
	def print_measure(self):
		measure_number = 'measure number=\"'+str(self._measure_number)+'\"'
		note_text=''
		for note in self.notes:
			if note.note_or_rest=='note':
				if note._dynamic:
					note_text+=note._dynamic.print_dynamic()
				note_text+=note.print_note()
			if note.note_or_rest=='rest':
				note_text+=note.print_rest()
		return tagify(measure_number, self.print_attributes()+'\n'+note_text,0,'measure')
#dots r[e]+r[e-1]



		
#----------------	
def get_note_name(note_str):
	accidentals = {'#':'sharp', 'b':'flat', '+': 'quarter-sharp','-':'quarter-flat'}
	alter = {'sharp':1, 'flat':-1, 'quarter-sharp':.5, 'quarter-flat':-.5}
	eighth_alter = {'_':'eighth_flat', '^':'eighth_sharp'}
	if len(note_str) == 1:
		accidental = 'natural'
		alter = 0
		note = note_str
		eighth_alter = None
	if len(note_str) == 2:
		if note_str[1] in accidentals:
			eighth_alter = None
			accidental = accidentals[note_str[1]]
			alter = alter[accidental]
			note = note_str[0]
		elif note_str[1] in eighth_alter:#C^
			eighth_alter = eighth_alter[note_str[1]]
			accidental = 'natural'
			alter = 0#!!actually .25!!
			note = note_str[0]
	if len(note_str) == 3:
		eighth_alter = eighth_alter[note_str[2]]
		accidental = accidentals[note_str[1]]
		alter = alter[accidental]
		note = note_str[0]
	return note, accidental, alter, eighth_alter
def eighth_to_char(string):
	eighth_alter = {'_':'eighth_flat', '^':'eighth_sharp'}#not needed...
	eighth_char = {'eighth_flat':'a', 'eighth_sharp':'q'}
	return eighth_char[string]
	
def closest_2(n):
	i=0
	j=0
	while j <= n:
		j = pow(2,i)
		i+=1
	return pow(2,i-2)/float(n)


def pitch_oct_to_midi(pitch, oct):
	base = (oct+1)*12
	both = base+pitch
	return both
class Note(Note_group_):
	
	#rhythm_dict={0.03125: '128th', 0.0625: '64th', 2:
	#'half', 4: 'whole', 0.5: 'eighth', 1: 'quarter', 0.25: '16th', 0.125: '32nd'}
	#rhythm_vals={'128th': 0.03125, '32nd': 0.125, '64th': 0.0625, 'half': 
	#	2, 'quarter': 1, 'whole': 4, '16th': 0.25, 'eighth': 0.5}
	
	
		
	white_keys = ['C','D','E','F','G','A','B']
	pitches_sharp = ['C','C#','D','D#','E','F','F#','G','G#','A','A#','B']
	pitches_flat = ['C','Db','D','Eb','E','F','Gb','G','Ab','A','Bb','B']
	ascending_24_tone = ['C', 'C+', 'C#', 'D-', 'D', 'D+', 'D#', 'E-', 'E', 'E+', 'F', 'F+', 
	'F#', 'G-', 'G', 'G+', 'G#', 'A-', 'A', 'A+', 'A#', 'B-', 'B', 'B+']
	descending_24_tone = ['C', 'C+', 'Db', 'D-', 'D', 'D+', 'Eb', 'E-', 'E', 'F-', 'F', 'F+', 
	'Gb', 'G-', 'G', 'G+', 'Ab', 'A-', 'A', 'A+', 'Bb', 'B-', 'B', 'B+']
	
	ascending_48_tone = ['C', 'C^', 'C+', 'C#_', 'C#', 'C#^', 'D-', 'D_', 'D', 'D^', 'D+', 'D#_', 'D#', 'D#^', 'E-', 'E_', 'E', 'E^', 'E+', 'F_', 'F', 'F^', 'F+', 'F#_', 'F#', 'F#^', 'G-', 'G_', 'G', 'G^', 'G+', 'G#_', 'G#', 'G#^', 'A-', 'A_', 'A', 'A^', 'A+', 'A#_', 'A#', 'A#^', 'B-', 'B_', 'B', 'B^', 'B+', 'C_']
	descending_48_tone = ['C', 'C^', 'C+', 'C_', 'Db', 'Db^', 'D-', 'Db_', 'D', 'D^', 'D+', 'D_', 'Eb', 'Eb^', 'E-', 'Eb_', 'E', 'E^', 'F-', 'E_', 'F', 'F^', 'F+', 'F_', 'Gb', 'Gb^', 'G-', 'Gb_', 'G', 'G^', 'G+', 'G_', 'Ab', 'Ab^', 'A-', 'Ab_', 'A', 'A^', 'A+', 'A_', 'Bb', 'Bb^', 'B-', 'Bb_', 'B', 'B^', 'B+', 'B_']
	
	
	def __init__(self, measure = None, index = None, note_group = None):
		#default_dict = {'pitch':'C','octave':'4', 'duration':1,'type':'eighth','stem':'up','voice':1,
		#	'note_or_rest':'note'}
		
		self._pitch = 'C'
		self._accidental = 'show'
		self._octave = 4
		self._type = 'eighth'
		self._value = .5
		self._duration = self._value#*120
		self._dots = 0
		
		#positioning----
		self._measure_position = 0
		self._end_position = 0
		self._part_position = 0
		self._index = 0
		#---------------
		
		self.stem = None#'up'
		self.voice = 1
		self.note_or_rest = 'note'
		
		self.upper_chord_member = 'no'
		
		self._grace = 'no'
		
		self._tie = 'no'
		self._slur = None
		self.beams = 1
		self.beam_status = None
		self.measure=measure
		self._dynamic = None
		self.note = 0
		
		self._articulations = []
		self._notations = []
		if note_group:
			note_group.members.append(self)
			note_group.print_beams()
		
		if measure:
			if self not in measure.notes:
				measure.notes.append(self)
		#measure.member(self,index)
		#add BEAMs...?  does it matter?
	def position(self, measure_position = None, part_position = None):
		self._measure_position = measure_position or self._measure_position
		self._part_position = part_position or self._part_position
		self._index = self._measure_position
		self._end_position = self._measure_position + self._value
		print 'Note measure position %s part position %s' % (self._measure_position, self._part_position)
		return self
	def chord(self, yes_no = 'yes'):
		self.upper_chord_member = yes_no
		self._value = 0
		self._duration = self._value
		return self
	def add_to_measure(self, measure, measure_number = None):
		measure.notes.append(self)
		#measure.order_measures()
		return self
	def add_to_part(self, part):
		part._floating_notes.append(self)
		self._part_for_adjusting = part#####ADJUSTMENT ADDITION:  FIX
		return self
	def type(self, new_type):
		print 'rhythmic type %s' % (new_type)
		self._type = new_type
		self._value = Rhythm.rhythm_vals[new_type]
		self._duration = self._value#*120
		if new_type == 'grace':
			self.grace()
		self.position()
		return self
	def pitch(self, new_pitch):
		print 'pitch at %s' % (new_pitch)
		self._pitch = new_pitch
		return self
	def transpose(self, transposition):
		self._pitch, self._octave = transpose((self._pitch, self._octave), transposition)
		return self
	def articulations(self,articulations = None):
		if articulations:
			if type(articulations) == list:
				for e in articulations:
					self._articulations.append(e)
			else:
				self._articulations.append(articulations)
		return self
	
	def notations(self, notations = None):
		if notations:
			self._notations.append(notations)
		return self
	def grace(self):
		self._grace = 'yes'
		self._type = 'eighth'
		self._value = 0
		self._duration = self._value#*120
		return self
	def octave(self, octave):
		print 'octave at %s' % (octave)
		self._octave = octave
		return self
	def dynamic(self, symbol, y_position = None, show_hide = None):
		if symbol:
			self._dynamic = Dynamic(self).symbol(symbol)
		if show_hide:
			self._dynamic._show = show_hide
		if y_position:
			self._dynamic.y_pos(y_position)
		return self
	def accidental(self,hide_show):
		self._accidental = hide_show
		return self
	def tie(self):
		self._tie = 'yes'
		return self
	def slur_start(self):
		self._slur = 'start'
		return self
	def slur_end(self):
		self._slur = 'stop'
		return self
	def stringify_dots(self):
		return (n+tag_self('dot'))*self._dots
	def number(self, number):
		self._index = number
		self._measure_number = number
		return self
	def print_beams(self):
		def make_beam(number):
			return n+tag_single('beam number=\"'+str(number+1)+'\"',self.beam_status,'beam')
		return string.joinfields(map(make_beam, range(self.beams)))
	def print_articulations(self):
		articulation_text = ''
		for articulation in self._articulations:
			articulation_text+=articulation.print_articulation()
		return articulation_text
	def print_notations(self):
		notation_text = ''
		for notation in self._notations:
			notation_text+=notation.print_notation()
		return notation_text
	
	def print_note(self):
		note_data = get_note_name(self._pitch)
		alter = tag_single('alter', str(note_data[2]))
		pitch = tagify('pitch',tag_single('step',note_data[0],0) + n + alter + n + tag_single('octave',self._octave,0),0)
		if int(self._value*4) == self._value*4: #stupid Finale shit: doesn't like floats for 'duration' if it is actualy an int
			self._duration = int(self._value*4)
		duration = tag_single('duration',self._duration,0)
		voice = tag_single('voice',str(self.voice),0)
		type = tag_single('type',self._type,0)
		if self._accidental == 'show':
			accidental = tag_single('accidental', str(note_data[1]))+n
			if note_data[3]:
				if note_data[3] == 'eighth_flat':
					x_offset = -12
					y_offset =  0
				if note_data[3] == 'eighth_sharp':
					x_offset = -12
					y_offset = -3
				if self._part_for_adjusting:
					clef = self._part_for_adjusting._clef
					#print 'OHHH YEAH CLEFFNESS'
				else:
					clef = treble_clef
				note_position = calculate_staff_position((self._pitch, self._octave), clef)+y_offset
				self.articulations(Text_over_note().font('MICRO3',24).text(eighth_to_char(note_data[3])).y_pos(note_position).x_pos(-15+x_offset))
		else:
			accidental = ''
		if self.stem:
			stem = tag_single('stem',self.stem,0)
		else:
			stem = ''
		if self._tie =='yes':
			tie = tagify('notations', tag_self('tied type="start"'))
		else:
			tie = ''
		if self._slur == 'start':
			slur = tagify('notations', tag_self('slur number="1" type="start"')) + n
		elif self._slur == 'stop':
			slur = tagify('notations', tag_self('slur number="1" type="stop"')) + n			
		else:
			slur = ''
		if self.upper_chord_member == 'yes':
			chord_text = tag_self('chord')+n
		else:
			chord_text = ''
		if self.beam_status:
			beams = n+self.print_beams()
		else:
			beams=''
		articulations = self.print_articulations()
		notations = self.print_notations()
		if self._grace == 'yes':
			grace = tag_self('grace slash="yes"')
		else:
			grace = ''
		#staff ADD
		dots = self.stringify_dots()
		return n+articulations+n+tagify('note',grace+n+chord_text+pitch+n+duration+n+voice+n+type+dots+n+accidental+stem+n+tie+slur+beams+notations,0)
	#def return_with_values(self, *args
class Chord_member(Note):
	def __init__(self, measure = None, index = None, note_group = None):
		#default_dict = {'pitch':'C','octave':'4', 'duration':1,'type':'eighth','stem':'up','voice':1,
		#	'note_or_rest':'note'}
			
		self._pitch = 'C'
		self._accidental = 'show'
		self._octave = 4
		self._type = 'eighth'
		self._value = .5
		self._duration = self._value#*120
		self._dots = 0
		
		#positioning----
		self._measure_position = 0
		self._part_position = 0
		self._index = 0
		self._end_position = 0
		#---------------
		
		self.stem = None#'up'
		self.voice = 1
		self.note_or_rest = 'note'
		
		self.upper_chord_member = 'yes'
		
		self._tie = 'no'
		self._slur = None
		self.beams = 1
		self.beam_status = None
		self.measure=measure
		self._dynamic = None
		self.note = 0
		
		self._articulations = []
		self._notations = []
		if note_group:
			note_group.members.append(self)
			note_group.print_beams()
		if measure:
			if self not in measure.notes:
				measure.notes.append(self)
		#measure.member(self,index)
		#add BEAMs...
class Plank(Note, Measure):
	def __init__(self, measure = None, index = None, note_group = None):
		#default_dict = {'pitch':'C','octave':'4', 'duration':1,'type':'eighth','stem':'up','voice':1,
		#	'note_or_rest':'note'}
		
		self._pitch = 'C'
		self._accidental = 'show'
		self._octave = 4
		self._type = 'eighth'
		self._value = .5
		self._duration = self._value#*120
		self._dots = 0
		
		#positioning----
		self._measure_position = 0
		self._end_position = 0
		self._part_position = 0
		self._length = 0
		self._index = 0
		#---------------
		self._floating_notes = []
		
		
		self.stem = None#'up'
		self.voice = 1
		self.note_or_rest = 'note'
		
		self.upper_chord_member = 'no'
		
		self._tie = 'no'
		self._slur = None
		self.beams = 1
		self.beam_status = None
		self.measure=measure
		self._dynamic = None
		self.note = 0
		
		self._articulations = []
		self._notations = []
		if note_group:
			note_group.members.append(self)
			note_group.print_beams()
		
		if measure:
			if self not in measure.notes:
				measure.notes.append(self)
	def position(self, part_position = None, end_position = None):#measure_position = None, part_position = None):
		#self._measure_position = measure_position or self._measure_position
		self._part_position = part_position or self._part_position
		self._index = self._measure_position
		self._end_position = end_position or self._end_position#self._measure_position + self._value
		self._length = self._end_position - self._part_position
		print 'Plank start %s Plank end %s' % (self._part_position, self._end_position)
		return self
	#def __repr__(self):
		
	def add_to_part(self, part):
		part._planks.append(self)
		#self._part_for_adjusting = part
		return self
	def attach_floating_note(self, note):
		if self.check_for_contiguous_measures():#possible to just check for proposed measure???
			self.order_measures().measures_info()
			i = 0
			current_value = 0
			while i < len(self.measures):
				
				#self.measures is LIST self._measure_infos is DICT!!!!
				if note._part_position >= current_value and note._part_position < current_value + self._measure_infos[i+1]:
					note.add_to_measure(self.measures[i]).position(measure_position = note._part_position - current_value)
				current_value += self._measure_infos[i+1]
				#print 'CURRENT VALUE',current_value, note._part_position - current_value
				i+=1
	def dynamic(self, symbol, y_position = None, part_for_adjustment = None):
		#print y_position, 'Y POSITION'
		if symbol:
			self._dynamic = Dynamic(self, y_position = y_position).symbol(symbol)
			self._dynamic._note_for_adjustment = self
		if y_position:
			self._dynamic.y_pos(y_position)
		if part_for_adjustment:
			self._dynamic._part_for_adjustment = part_for_adjustment
		return self
	def chop(self, part):
		if part.check_for_contiguous_measures():#make sure there are contiguous measures
			length = self.position()._length
			i = 0
			current_value = 0
			used_values = 0
			while i < len(part.measures):
				just_measure_value = part.measures_info()._measure_infos[i+1]
				if current_value >= self._part_position:
					place_in_measure = (current_value - just_measure_value + self._part_position)%just_measure_value#,'current - part pos'
					#print place_in_measure, 'place IN MEASURE'
					current_measure = current_value - just_measure_value
					next_value = current_value + just_measure_value
					#if self._dynamic:#########SOME SHIT ABOUT STANDARDIZING -- use dynamic instance or dynamic symbol???????????
					#	if self._dynamic._show == 'yes':
					#		dyn = self._dynamic._symbol
					#	else:
					#		dyn = None
						
					#else:
					#	dyn = None
					dyn = self._dynamic
					
					if length <= just_measure_value  and (place_in_measure + length) <= just_measure_value:
						Note_group_().notes_for_value_B(length,[self._pitch,self._octave],part=part, start = self._part_position, end_tie = 'no', dynamic = dyn, articulations = self._articulations)
						print 'Case 1: the plank is shorter than a measure!', (place_in_measure + self._end_position), next_value
						break
					if (place_in_measure + length) > just_measure_value and (current_value - just_measure_value) < self._part_position:#  and (place_in_measure + self._end_position) < (current_value + just_measure_value):
						Note_group_().notes_for_value_B(just_measure_value - place_in_measure,[self._pitch,self._octave],direction = 'forwards', part=part, start = self._part_position+used_values, 
						end_tie = 'yes', dynamic = self._dynamic, articulations = self._articulations)
						#################Bug fix for begining of measure start
						#if used_values == 0 and place_in_measure == 0:		01.09.07 -- commented out
						#	current_value += just_measure_value		01.09.07 -- commented out
						#################
						print place_in_measure, 'PLACE IN MEASURE'
						used_values+=(just_measure_value - place_in_measure)
						print 'Case 2:  middle, kinda', place_in_measure
					elif used_values <= length and (used_values + just_measure_value) <= length:
						if used_values+just_measure_value == length:
							end_tie = 'no'
						else:
							end_tie = 'yes'
							
						####POTENTIALLY A SHITTY CHEEP FIX
						if self._part_position % just_measure_value == 0:
							Note_group_().notes_for_value_B(just_measure_value,[self._pitch,self._octave],part=part, start = current_value, end_tie = end_tie)
						else:
							Note_group_().notes_for_value_B(just_measure_value,[self._pitch,self._octave],part=part, start = current_value - just_measure_value, end_tie = end_tie)
						####POTENTIALLY A SHITTY CHEEP FIX
						print 'Case 3: the middle of plank takes up a measure!'
						#break
						used_values+=just_measure_value
					if used_values >= length:
						break
					
					if next_value > self._end_position :
						Note_group_().notes_for_value_B(length-used_values,[self._pitch,self._octave],part=part, start = current_value, end_tie = 'no')
						print 'Case 4 ending'
						used_values+=just_measure_value
						#break
					if used_values >= length:
						break
					part.measures[i].order_notes()
				current_value += just_measure_value
				i+=1
		return self
				
class Rest(Note):
	def __init__(self, measure, index = None, note_group = None):
		self._duration = 1
		self._type = 'quarter'
		self._value = .5
		self._duration = self._value#*120
		self._dots = 0
		
		#positioning----
		self._measure_position = 0
		self._part_position = 0
		self._index = 0
		#---------------
		
		self.voice = 1
		self.note_or_rest='rest'
		self.beams = []
		
		self.measure=measure
		self._dynamic = None
		if note_group:
			note_group.members.append(self)
		elif self not in measure.notes:
			measure.notes.append(self)
		measure.member(self,index)
	def print_note(self):
		if int(self._value*4) == self._value*4:
			self._duration = int(self._value*4)
		duration = tag_single('duration',self._duration,0)
		voice = tag_single('voice',str(self.voice),0)
		type = tag_single('type',self._type,0)
		#staff ADD
		return n+tagify('note','<rest/>'+'\n'+duration+'\n'+voice+'\n'+type,0)
	print_rest=print_note
class Articulation(Note):
	def print_articulation(self):
		self.extra_data = tag_self('sound dynamics=\"'+str(self.level)+'\"')
		self.direction_type = tagify('direction-type',self.articulation_data)+n+self.extra_data
		placement = tagify('direction placement=\"'+self.placement+'\"',self.direction_type,0,'direction')
		return placement
	def position(self, measure_position = None, part_position = None):
		self._measure_position = measure_position or self._measure_position
		self._part_position = part_position or self._part_position
		self._index = self._measure_position
		#self._end_position = self._measure_position + self._value
		print 'Articulation measure position %s part position %s' % (self._measure_position, self._part_position)
		return self
	def y_pos(self, number):
		if number:
			self._y_position = number
		return self
	def x_pos(self, number):
		if number:
			self._x_position = number
		return self
		
class Dynamic(Articulation):
	dynamics = ['pppp','ppp','pp','p','mp','mf','f','ff','fff','ffff']
	sound_levels = {'pppp':11,'ppp':32,'pp':40,'p':54,'mp':69,'mf':83,'f':98,
	'ff':112, 'fff':127, 'ffff':141}
	def __init__(self, note = None, note_group=None, y_position = None, show_hide = None, 
	note_for_adjustment = None, part_for_adjustment = None):
		self._type = 'dynamic'
		self.placement = 'below'                                      
		self._symbol = 'mf'
		self._y_position = y_position
		self.note=note
		#note._articulations.append(self)
		if show_hide:
			self._show = show_hide
		else:
			self._show = 'yes'
		#positioning----
		self._measure_position = 0
		self._end_position = 0
		self._part_position = 0
		self._index = 0
		#---------------
		self._note_for_adjustment = note_for_adjustment
		self._part_for_adjustment = part_for_adjustment
	def symbol(self, symbol):
		self._symbol = symbol
		return self
	
	def hide(self):
		self._show = 'no'
		return self
	
	def adjustment(self, note_for_adjustment = None, part_for_adjustment = None, offset = -30):
		#if note_for_adjustment:
		#	self._note_for_adjustment = note_for_adjustment
		#if part_for_adjustment:
		#	self._part_for_adjustment = part_for_adjustment
		#print self._part_for_adjustment, 'PART FOR ADJUSTMENT'
		note_position = calculate_staff_position((self._note_for_adjustment._pitch, self._note_for_adjustment._octave), self._part_for_adjustment._clef)
		adjusted_placement = int(round(general_functions.clip(note_position,(-150,-60)) + offset))#stupid Finale shit: doesn't like floats for offset amount; btw, what is the reasoning behind these numbers???
		#print note_position, 'NOTE POSITION', adjusted_placement, 'NOTE PLACEMENT'
		self.y_pos(adjusted_placement)
		return self
	
	def print_articulation(self):
		self.adjustment()
		if self._show == 'yes':
			level = Dynamic.sound_levels[self._symbol]
			if self._y_position:
				#print "yPOSITIOn"
				articulation_data = tagify('dynamics default-y=\"'+str(int(self._y_position))+'\"',tag_self(self._symbol),0,'dynamics')
			else:
				articulation_data = tagify('dynamics',tag_self(self._symbol),0)
				#print 'No Y POSITION'
			offs = [0,0,0, -2, -2, -2]
			offs = {'pppp':-3,'ppp':-2.5,'pp':-1.8,'p':0,'mp':-1.2,'mf':-.8,'f':0,
			'ff':-1.2, 'fff':-2.2, 'ffff':-2.6}
			x_adjustment = tag_single('offset', str(offs[self._symbol]))####AHHHH No floats!
			extra_data = tag_self('sound dynamics=\"'+str(level)+'\"')
			self.direction_type = tagify('direction-type',articulation_data)+n+x_adjustment+n+extra_data
			placement = '\n'+tagify('direction placement=\"'+self.placement+'\"',self.direction_type,0,'direction')
			#placement = 'YES'
		elif self._show == 'no' or self._show == None:
			placement = ''
		return placement
	print_dynamic = print_articulation
class Text_over_note(Articulation):
	def __init__(self, note = None):
		self.placement = 'below'
		self._y_position = 0
		self._x_position = 0
		
		#self.deviation = 0
		self._text = 'default'
		
		self._font = 'Times New Roman'
		self._font_size = 11
		
		
		#self.articulation_data = '<words default-y=\"'+str(self._y_position)+'\" font-family=\"'+self._font+'\" font-size=\"'+str(self._font_size)+'\" relative-x=\"'+str(self.x_position)+'\">'+str(self.deviation)+'</words>'
		self.extra_data = ''
		
		self.note=note
		#note._articulations.append(self)
	def text(self, text = None):
		self._text = text
		return self
	def font(self, font = None, font_size = None):
		if font:
			self._font = font
		if font_size:
			self._font_size = font_size
		return self
	
	def print_text(self):#= Articulation.print_articulation
		articulation_data = '<words default-y=\"'+str(self._y_position)+'\" font-family=\"'+self._font+'\" font-size=\"'+str(self._font_size)+'\" relative-x=\"'+str(self._x_position)+'\">'+str(self._text)+'</words>'
		self.direction_type = tagify('direction-type',articulation_data)+n#+extra_data
		placement = '\n'+tagify('direction placement=\"'+self.placement+'\"',self.direction_type,0,'direction')
			
		return placement
	
	print_articulation = print_text

class Cents(Text_over_note):
	print_cents = Articulation.print_articulation
	pass
class Notations(Articulation):
	def __init__(self, note=None, note_group=None):
		self._type = 'fermata'
		self._position = 'upright'
		self._show = 'yes'
	def type(self, type):
		self._type = type
		return self
	def print_notation(self):
		if self._show == 'yes':
			placement = tagify('notations',tag_self('fermata type="'+self._position+'"'))
		elif self._show == 'no':
			placement = ''
		return placement

#auto-accidentalize:  flats:  any natural -> flat; flat -> natural - of same.
		#No augmented intervals:
		#	aug 2nd: Ab-B, Gb-A, Db-E
		#	dim 3rd: B-Db, E-Gb
		#	5ths:  B-Gb
#BUGs to fix:
#	1.  Plank slicing algorithm. 			 maybe reverse if before 3rd beat??
#		VARS:
#			if start is before mid-measure (inv. barline)
#			if start is float
#			if end is float
#x.  give each measure and each note/rest an index, an ID and a Value
#x.	give each note entry an index within the measure and 
#	entry from beginning of piece (possible to redo barlines?)
#.	Refer to measures by Number and by Part
#	Refer to beats by distance from beginning...
#	work on 'tied across barline' notes
#	articulations (>,-,->,., etc.)
#.	tuplets

#class Hairpin:
#	def __init__(self):
#		note_group.members[0]
	
