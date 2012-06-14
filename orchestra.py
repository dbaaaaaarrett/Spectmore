from probability import *
import general_functions, random, putil
from mxml import *


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
	octave = int((int(midi_note)-middle_c)/12)+4########WOW!!!! FUNDAMENTAL BUG.  midi_note must be made an int before the other stuff
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
	
	
class Instrument(Part):
	
	def __init__(self):
		self._transposition = 0
		self._range_conservative = [['C',3],['C',4]]
		self._range = [['C',1],['C',8]]
		
	def group(self, start_or_stop = None, group_name = None, group_abbrev = None, bracket = 'yes'):
		self._group = start_or_stop
		self._group_name = group_name
		self._group_abbrev = group_abbrev
		self._bracket = bracket
		return self
	def name(self, name, abbrev = None):
		self._name, self._abbreviation = name, abbrev
		return self
	def clef(self, clef):
		self._clef = clef
		return self
	def transposition(self, trans):
		self._transposition = trans
		return self
	def range(self, range):
		self._range = range
		return self
	def range_preferred(self, range):
		self._range_preferred = range
		return self
	def microtones(self, micro):
		self._microtones = micro
		return self
	#def setup(self, name = None, clef = None, transposition = None, range_conservative = None, range = None, microtones = None):
	#	self._
	#	return self
	def midify(self):
		self._low = note_and_octave_to_midi(self._range[0])
		self._high = note_and_octave_to_midi(self._range[1])
		self._preferred_high = note_and_octave_to_midi(self._range_preferred[1])#OUCH!  was a dumb mistake before
		self._preferred_low = note_and_octave_to_midi(self._range_preferred[0])
		return self
	
	def arbitrary_pitch_point(self, (note,octave)):
		midi_val = note_and_octave_to_midi((note,octave)) 
		self._arbitrary_pitch_point = midi_val
		return self
		
	def average(self):
		try:
			if self._arbitrary_pitch_point:
				pass
		except AttributeError:
			self._arbitrary_pitch_point = None
		#############
		if self._arbitrary_pitch_point:
			self._average_range = self._arbitrary_pitch_point
			self._preferred_average_range = self._arbitrary_pitch_point
		#############
		else:
			self._average_range = (self._low + self._high)/2.
			self._preferred_average_range = (self._preferred_low + self._preferred_high)/2
		#self._average_range, self._preferred_average_range
		return self
	def part(self):
		self._part = Part()
		return self
	def Plank(self):
		return Plank().add_to_part(self._part)
	
	def choir_weights(self, weight_key):
		self._weight_key = weight_key
		self._choir_weight = self._weight_key[self._choir]
		if not self._stat_bundle:
			self._stat_bundle = Statistic_group(self).add(Parameter_weight().value(self._choir_weight))
		
	def add_weight(self, value):
		value = int(round(value))
		if self._stat_bundle:
			self._stat_bundle.add(Parameter_weight().value(value))
		else:
			self._stat_bundle = Statistic_group(self).add(Parameter_weight().value(value))
		return self
	
	def strip_weights(self):
		self._stat_bundle = Statistic_group(self)
		return self
	
	def initialize(self):
		self.midify()
		self.group()
		self.average()
		
		self._stat_bundle = None
		#self.choir_weights(choir_weights)
		
		Part.serial_number += 1
		self.number = Part.serial_number
		self.staves = 1
		self.midi_channel = Part.serial_number
		self.measures = []
		self._measure_numbers = []
		self._starting_measure_number = 1
		self._floating_notes = []
		self._planks = []
		#self._clef = treble_clef
		self._group, self._group_name, self._group_abbrev, self._bracket, self._group_barline, self._bracket = None, None, None, None, 'yes','yes'
		
		self._program = 1
		
		############gives each object a min and max length attribute of None if one's not provided...
		try:
			if self._min_max_length:
				pass
		except AttributeError:
			self._min_max_length = None
		############gives each object a min distance from last note attribute of None if one's not provided...
		try:
			if self._min_distance_from_last_note:
				pass
		except AttributeError:
			self._min_distance_from_last_note = 0
		#############
		
		############Gives everyone a 'transposed clef'
		try:
			if self._transposed_clef:
				pass
		except AttributeError:
			self._transposed_clef = self._clef
		############
		
		self._partial_components = []
		
		self.clef(self._clef)
		self.add()
		
		return self
		
	def microtonal_capability_in_range(self, pitch):
		midi_pitch = pitch#note_and_octave_to_midi(pitch)
		if type(self._microtones) == str:
			return self._microtones
		elif self._microtones == None:
			return None
		#print self._microtones
		if midi_pitch >= self._low and midi_pitch <= self._high:#######protection?
			for entry in self._microtones:
				lower_bounds = note_and_octave_to_midi(entry[0])
				upper_bounds = note_and_octave_to_midi(entry[1])
				if midi_pitch >= lower_bounds and midi_pitch <= upper_bounds:
					return entry[2]

			
#[[['G',3],['B',4],'quarter'],[etc.		
#STRINGS	###############################		STRINGS
class Violin(Instrument):
	def __init__(self):
		self._name, self._abbreviation = 'Violin','Vln.'
		self._clef = treble_clef
		self._transposition = 0
		self._range_conservative = [['C',3],['C',4]]
		self._range_preferred =  [['G',3],['E',6]]
		self._range = [['G',3],['B',7]]
		self._choir = 'strings'
		self._microtones = 'all'
		self.initialize()
		
class Viola(Instrument):
	def __init__(self):
		self._name, self._abbreviation = 'Viola','Vla.'
		self._clef = alto_clef
		self._transposition = 0
		self._range_conservative = [['C',3],['C',4]]
		self._range_preferred =  [['C',3],['A',5]]
		self._range = [['C',3],['D',6]]#	was [A,6]
		self._choir = 'strings'
		self._microtones = 'all'
		self.initialize()
		
class Cello(Instrument):
	def __init__(self):
		self._name, self._abbreviation = 'Cello','Cl.'
		self._clef = bass_clef
		self._transposition = 0
		self._range_conservative = [['C',3],['C',4]]
		self._range_preferred =  [['C',2],['A',3]]
		self._range = [['C',2],['C',5]]#	was [E,6]
		self._choir = 'strings'
		self._microtones = 'all'
		self.initialize()
		
class Double_bass(Instrument):
	def __init__(self):
		self._name, self._abbreviation = 'Contrabass','Cbs.'
		self._clef = bass_clef
		self._transposition = 12
		self._range_conservative = [['C',3],['C',4]]
		self._range_preferred =  [['E',1],['D',2]]
		self._range = [['E',1],['G',2]]#	was [G,5]
		self._choir = 'strings'
		self._microtones = 'all'
		self.arbitrary_pitch_point(['E',1])
		self.initialize()
		
#WINDS	###############################		WINDS		
class Picolo(Instrument):
	def __init__(self):
		self._name, self._abbreviation = 'Picolo','Pc.'
		self._clef = bass_clef
		self._transposition = -12
		self._range_conservative = [['C',3],['C',4]]
		self._range = [['E',5],['C',7]]
		self._range_preferred =  [['E',5],['C',7]]
		self._choir = 'winds'
		self._microtones = 'quarter'
		self.initialize()
		
class Flute(Instrument):
	def __init__(self):
		self._name, self._abbreviation = 'Flute','Fl.'
		self._clef = treble_clef
		self._transposition = 0
		self._range_conservative = [['C',3],['C',4]]
		self._range = [['C',4],['D',6]]
		self._range_preferred =  [['C',4],['D',6]]
		self._choir = 'winds'
		self._microtones = 'quarter'
		self.initialize()
		
class Alto_flute(Instrument):
	def __init__(self):
		self._name, self._abbreviation = 'Alto Flute','Alto Fl.'
		self._clef = treble_clef
		self._transposition = 5
		self._range_conservative = [['C',3],['C',4]]
		self._range = [['G',3],['G',6]]
		self._range_preferred =  [['G',3],['G',6]]
		self._choir = 'winds'
		self._microtones = 'quarter'
		self.initialize()
		
class Oboe(Instrument):
	def __init__(self):
		self._name, self._abbreviation = 'Oboe','Ob.'
		self._clef = treble_clef
		self._transposition = 0
		self._range_conservative = [['C',3],['C',4]]
		self._range = [['Bb',3],['C',5]]
		self._range_preferred =  [['Bb',3],['C',5]]
		self._choir = 'winds'
		self._microtones = 'quarter'
		self.initialize()
		
class English_horn(Instrument):
	def __init__(self):
		self._name, self._abbreviation = 'English Horn','E. Hn.'
		self._clef = treble_clef
		self._transposition = 7
		self._range_conservative = [['C',3],['C',4]]
		self._range = [['E',3],['E',6]]
		self._range_preferred =  [['E',3],['E',5]]		
		self._choir = 'winds'
		self._microtones = 'quarter'
		self.initialize()
		
class Clarinet(Instrument):
	def __init__(self):
		self._name, self._abbreviation = 'Clarinet','Cl.'
		self._clef = treble_clef
		self._transposition = 2
		self._range_conservative = [['C',3],['C',4]]
		self._range = [['D',3],['Bb',5]]
		self._range_preferred =  [['D',3],['Bb',5]]
		self._choir = 'winds'
		self._microtones = [[['D',3],['G',3],'semi'],[['G',3],['Bb',5],'quarter']]#'quarter'
		self.initialize()
		
Clarinet_in_Bb = Clarinet

class Bass_clarinet(Instrument):
	def __init__(self):
		self._name, self._abbreviation = 'Bass Clarinet','Bass Cl.'
		self._clef = bass_clef
		self._transposed_clef = treble_clef
		self._transposition = 14
		self._range_conservative = [['C',3],['C',4]]
		self._range = [['Eb',2],['A',4]]
		self._range_preferred =  [['Eb',2],['A',4]]
		self._choir = 'winds'
		self._microtones = [[['Eb',2],['Gb',2],'semi'],[['G',2],['A',4],'quarter']]#'quarter'#G2-F5
		self.initialize()
		
class Contrabass_clarinet(Instrument):
	def __init__(self):
		self._name, self._abbreviation = 'Contrabass Clarinet',"C'Bass Cl."
		self._clef = bass_clef
		self._transposed_clef = treble_clef
		self._transposition = 26
		self._range_conservative = [['C',3],['C',4]]
		self._range = [['C',1],['C',4]]
		self._range_preferred =  [['C',1],['C',4]]
		self._choir = 'winds'
		self._microtones = 'quarter'
		self.initialize()
		
class Bassoon(Instrument):
	def __init__(self):
		self._name, self._abbreviation = 'Bassoon','Bsn.'
		self._clef = bass_clef
		self._transposition = 0
		self._range_conservative = [['C',3],['C',4]]
		self._range = [['Bb',2],['D',4]]
		self._range_preferred =  [['Bb',2],['D',4]]
		self._choir = 'winds'
		self._microtones = 'quarter'
		self.initialize()
		
class Contrabassoon(Instrument):
	def __init__(self):
		self._name, self._abbreviation = 'Contrabassoon','Cbsn.'
		self._clef = bass_clef
		self._transposition = 12
		self._range_conservative = [['C',3],['C',4]]
		self._range = [['Bb',1],['D',3]]
		self._range_preferred =  [['Bb',1],['D',3]]
		self._choir = 'winds'
		self._microtones = 'quarter'
		self.initialize()

class Soprano_saxophone(Instrument):
	def __init__(self):
		self._name, self._abbreviation = 'Soprano Saxophone','Sop. Sax'
		self._clef = treble_clef
		self._transposition = 2
		self._range_conservative = [['C',3],['C',4]]
		self._range = [['Ab',3],['Eb',6]]
		self._range_preferred =  [['Ab',3],['Eb',6]]
		self._choir = 'winds'
		self._microtones = None
		self.initialize()

class Alto_saxophone(Instrument):
	def __init__(self):
		self._name, self._abbreviation = 'Alto Saxophone','Alt. Sax'
		self._clef = treble_clef
		self._transposition = 9
		self._range_conservative = [['C',3],['C',4]]
		self._range = [['Db',3],['A', 5]]
		self._range_preferred =  [['Db',3],['A',5]]#49-81
		self._choir = 'winds'
		self._microtones = None
		self.initialize()

class Baritone_saxophone(Instrument):
	def __init__(self):
		self._name, self._abbreviation = 'Baritone Saxophone','Bari. Sax'
		self._clef = treble_clef
		self._transposition = 21
		self._range_conservative = [['C',3],['C',4]]
		self._range = [['Db',2],['A',4]]
		self._range_preferred =  [['Db',2],['A',4]]#37-69
		self._choir = 'winds'
		self._microtones = None
		self.initialize()

#BRASS	###############################		BRASS		

class French_horn(Instrument):
	def __init__(self):
		self._name, self._abbreviation = 'French Horn','Fr. Hn.'
		self._clef = treble_clef
		self._transposition = 7
		self._range_conservative = [['C',3],['C',4]]
		self._range = [['B',1],['D',4]]######?????????
		self._range_preferred =  [['F#',2],['D',4]]####???????
		self._choir = 'brass'
		self._microtones = 'quarter'
		self.initialize()
		
class Trumpet(Instrument):
	def __init__(self):
		self._name, self._abbreviation = 'Trumpet','Tpt.'
		self._clef = treble_clef
		self._transposition = 0
		self._range_conservative = [['C',3],['C',4]]
		self._range = [['F#',3],['A',5]]
		self._range_preferred = [['C',4],['A',5]]
		self._choir = 'brass'
		self._microtones = 'quarter'
		self.initialize()
		
class Trombone(Instrument):
	def __init__(self):
		self._name, self._abbreviation = 'Trombone','Tbn.'
		self._clef = bass_clef
		self._transposition = 0
		self._range_conservative = [['C',3],['C',4]]
		self._range = [['E',2],['F',4]]
		self._range_preferred = [['E',2],['F',4]]
		self._choir = 'brass'
		self._microtones = 'all'
		self.initialize()
		
class Bass_Trombone(Instrument):
	def __init__(self):
		self._name, self._abbreviation = 'Bass Trombone','Bass Tbn.'
		self._clef = bass_clef
		self._transposition = 0
		self._range_conservative = [['C',3],['C',4]]
		self._range = [['Bb',1],['C',4]]
		self._range_preferred = [['Bb',1],['C',4]]
		self._choir = 'brass'
		self._microtones = 'all'
		self.initialize()
		
class Tuba(Instrument):
	def __init__(self):
		self._name, self._abbreviation = 'Tuba','Tuba'
		self._clef = bass_clef
		self._transposition = 0
		self._range_conservative = [['C',3],['C',4]]
		self._range = [['D',1],['E',3]]
		self._range_preferred = [['D',1],['E',3]]
		#self._min_distance_from_last_note = 5
		self._choir = 'brass'
		self._microtones = 'quarter'
		self.initialize()
		
#PERCUSSION	###############################		PERCUSSION

class Vibraphone(Instrument):
	def __init__(self):
		self._name, self._abbreviation = 'Vibraphone','Vib.'
		self._clef = treble_clef
		self._transposition = 0
		self._range_conservative = [['C',3],['C',4]]
		self._range = [['F',3],['C',6]]
		self._range_preferred = [['F',3],['F',6]]#was C6
		self._choir = 'percussion'
		self._microtones = None
		self._min_max_length = [0,20]
		self.initialize()

class Vibraphone_R(Instrument):
	def __init__(self):
		self._name, self._abbreviation = 'Vibraphone','Vib.'
		self._clef = treble_clef
		self._transposition = 0
		self._range_conservative = [['C',3],['C',4]]
		self._range = [['C',5],['F',6]]
		self._range_preferred = [['C',5],['F',6]]#was C6
		self._choir = 'percussion'
		self._microtones = None
		self._min_max_length = [0,20]
		self.initialize()

class Vibraphone_L(Instrument):
	def __init__(self):
		self._name, self._abbreviation = 'Vibraphone','Vib.'
		self._clef = treble_clef
		self._transposition = 0
		self._range_conservative = [['C',3],['C',4]]
		self._range = [['F',3],['B',4]]
		self._range_preferred = [['F',3],['B',4]]#was C6
		self._choir = 'percussion'
		self._microtones = None
		self._min_max_length = [0,20]
		self.initialize()


class Timpani(Instrument):
	def __init__(self):
		self._name, self._abbreviation = 'Timpani','Timp.'
		self._clef = bass_clef
		self._transposition = 0
		self._range_conservative = [['C',3],['C',4]]
		self._range = [['C',2],['C',4]]
		self._range_preferred = [['C',2],['C',4]]
		self._choir = 'percussion'
		self._microtones = 'all'
		self._min_distance_from_last_note = 32
		self.arbitrary_pitch_point(['C',2])
		self.initialize()
		
#KEYBOARD	###############################		KEYBOARD

class Piano_RH(Instrument):
	def __init__(self):
		self._name, self._abbreviation = 'Piano','Pno.'
		self._clef = treble_clef
		self._transposition = 0
		self._range_conservative = [['C',3],['C',4]]
		self._range = [['C',4],['C',8]]
		self._range_preferred = [['C',6],['C',8]]
		self._choir = 'keyboard'
		self._microtones = None
		self._min_max_length = [0,20]
		self.initialize()
		
class Piano_LH(Instrument):
	def __init__(self):
		self._name, self._abbreviation = 'Piano','Pno.'
		self._clef = bass_clef
		self._transposition = 0
		self._range_conservative = [['C',3],['C',4]]
		self._range = [['A',0],['C',4]]
		self._range_preferred = [['A',0],['C',1]]
		self._choir = 'keyboard'
		self._microtones = None
		self._min_max_length = [0,20]
		#self.arbitrary_pitch_point(['A',0])
		self.initialize()
		
#RHODES	###############################	C2 to C6?

class Rhodes_RH(Instrument):
	def __init__(self):
		self._name, self._abbreviation = 'Piano','Pno.'
		self._clef = treble_clef
		self._transposition = 0
		self._range_conservative = [['C',3],['C',4]]
		self._range = [['C',5],['C',7]]
		self._range_preferred = [['C',4],['C',7]]
		self._choir = 'keyboard'
		self._microtones = None
		self._min_max_length = [0,20]
		self.initialize()
		
class Rhodes_LH(Instrument):
	def __init__(self):
		self._name, self._abbreviation = 'Piano','Pno.'
		self._clef = bass_clef
		self._transposition = 0
		self._range_conservative = [['C',3],['C',4]]
		self._range = [['C',1],['B',3]]
		self._range_preferred = [['C',1],['B',3]]
		self._choir = 'keyboard'
		self._microtones = None
		self._min_max_length = [0,20]
		self.arbitrary_pitch_point(['A',0])
		self.initialize()
		
#HARP

class Harp_RH(Instrument):
	def __init__(self):
		self._name, self._abbreviation = 'Harp','Harp.'
		self._clef = treble_clef
		self._transposition = 0
		self._range_conservative = [['C',3],['C',4]]
		self._range = [['C',4],['G#',7]]
		self._range_preferred = [['C',6],['G#',7]]
		self._choir = 'harp'
		self._microtones = None
		self._min_max_length = [0,20]
		self.initialize()
		
class Harp_LH(Instrument):
	def __init__(self):
		self._name, self._abbreviation = 'Harp','Harp.'
		self._clef = bass_clef
		self._transposition = 0
		self._range_conservative = [['C',3],['C',4]]
		self._range = [['B',0],['C',4]]####spelled Cb!
		self._range_preferred = [['B',0],['C',1]]
		self._choir = 'harp'
		self._microtones = None
		self._min_max_length = [0,20]
		self.initialize()

#GENERIC

class Generic(Instrument):
	def __init__(self):
		self._name, self._abbreviation = 'Default','Default.'
		self._clef = treble_clef
		self._transposition = 0
		self._range_conservative = [['C',3],['C',4]]
		self._range = [['C',3],['C',6]]
		self._range_preferred =  [['C',3],['C',6]]
		self._choir = 'percussion'
		self._microtones = 'all'
		self.initialize()
#VOICE

class Soprano(Instrument):
	def __init__(self):###some text to sing??  take from rec.?
		self._name, self._abbreviation = 'Soprano','Sop.'
		self._clef = treble_clef
		self._transposition = 0
		self._range_conservative = [['C',3],['C',4]]
		self._range = [['F',4],['B',4]]
		self._range_preferred = [['F',3],['B',5]]
		self._choir = 'percussion'
		self._microtones = None
		self._min_max_length = [2,10]
		self.initialize()

#ACCORDION

class Accordion(Instrument):
	def __init__(self):
		self._name, self._abbreviation = 'Accordion','Acc..'
		self._clef = bass_clef
		self._transposition = 0
		self._range_conservative = [['C',3],['C',4]]
		self._range = [['B',0],['C',4]]
		self._range_preferred = [['E',1],['D#',5]]
		self._choir = 'percussion'
		self._microtones = None
		self._min_max_length = [0,20]
		self.initialize()

#GUITAR

class Guitar(Instrument):
	def __init__(self):
		self._name, self._abbreviation = 'Guitar','Guit..'
		self._clef = treble_clef
		self._transposition = 12
		self._range_conservative = [['C',3],['C',4]]
		self._range = [['E',2],['C',5]]
		self._range_preferred = [['E',2],['D',5]]
		self._choir = 'percussion'
		self._microtones = None
		self._min_max_length = [0,20]
		self.initialize()

#BASS GUITAR

class Bass_guitar(Instrument):
	def __init__(self):
		self._name, self._abbreviation = 'Bass Guitar','B.Guit.'
		self._clef = bass_clef
		self._transposition = 12
		self._range_conservative = [['C',3],['C',4]]
		self._range = [['E',1],['E',3]]
		self._range_preferred = [['E',1],['E',3]]
		self._choir = 'percussion'
		self._microtones = None
		self._min_max_length = [0,20]
		self.initialize()


#class Weight(Instrument):
#	def __init__(self):
#		self._choir_balance = [1.,1.,1.,1.,1.,1.]
		
#experimental_group = [Generic().name('1','1').range_preferred([['G',3],['E',6]]),Generic().name('2','2'),Generic().name('3','3').range_preferred([['E',2],['C',6]]),Generic().name('4','4').range_preferred([['E',2],['C',6]])]
		
#winds = [Flute().name('1','1').group('start','2 Flutes','2 Fls.'),Flute().name('2','2').group('stop'),Alto_flute(),Oboe().name('1','1').group('start','2 Oboes','2 Obs.'),Oboe().name('2','2').group('stop'),English_horn(),Clarinet(),Clarinet(),
#Bass_clarinet(), Contrabass_clarinet(), Bassoon(), Bassoon(), Contrabassoon()]

#brass = [French_horn(),French_horn().clef('bass'),French_horn(),French_horn().clef('bass'),
#Trumpet(),Trumpet(),Trumpet(),Trombone(),Trombone(),Bass_Trombone(),Tuba()]

#perc_other = [Harp_RH().name('','').group('start','Harp','Harp'), Harp_LH().name('','').group('stop'), Piano_RH().name('','').group('start','Piano','Pno.'),Piano_LH().name('','').group('stop'), Vibraphone(), Timpani()]

#strings = [Violin().name('1-4','1-4').group('start','Violins I', 'Vlns I'), Violin().name('5-8','5-8'), Violin().name('9-12','9-12').group('stop'),
#Violin().name('1-4','1-4').group('start','Violins II', 'Vlns II'), Violin().name('5-8','5-8'), Violin().name('9-12','9-12').group('stop'), 
#Viola().name('1-5','1-5').group('start','Violas','Vlas.'), Viola().name('6-10','6-10').group('stop'), 
#Cello().name('1-4','1-4').group('start','Cellos','Cls.'), Cello().name('5-8','5-8').group('stop'), 
#Double_bass().name('1-3','1-3').group('start','Contrabasses','Cbs.'),Double_bass().name('4-6','4-6').group('stop')]

#full_orchestra = winds+brass+perc_other+strings#experimental_group

#chamber_orchestra = [Flute().group('start'), English_horn(), Clarinet(), Bass_clarinet().group('stop'), 
#French_horn().group('start'), Trombone(), Bass_Trombone().group('stop'),
#Harp_RH().name('','').group('start','Harp','Harp'), Harp_LH().name('','').group('stop'), 
#Piano_RH().name('','').group('start','Piano','Pno.'),Piano_LH().name('','').group('stop'), 
#Violin().group('start'), Viola(), Cello(), Double_bass().group('stop')]

#chamber_orchestra = [Bass_clarinet().group('start'),  Contrabass_clarinet(),
#Bassoon(), Contrabassoon().group('stop'),
#Trombone().group('start'), Bass_Trombone(), Tuba().group('stop'),
#Harp_RH().name('','').group('start','Harp','Harp'), Harp_LH().name('','').group('stop'), 
#Piano_RH().name('','').group('start','Piano','Pno.'),Piano_LH().name('',''), Timpani().group('stop'),
#Violin().group('start'), Violin(), Viola(), Cello(), Double_bass().group('stop')]#THIS WAS USED FOR DERIVATION V.

#chamber_orchestra = [Bass_clarinet().group('start'),  Contrabass_clarinet(),
#Bassoon(), Contrabassoon().group('stop'),
#Trombone().group('start'), Bass_Trombone(), Tuba().group('stop'),
#Harp_RH().name('','').group('start','Harp','Harp'), Harp_LH().name('','').group('stop'), 
#Piano_RH().name('','').group('start','Piano','Pno.'),Piano_LH().name('','').group('stop'), Timpani(),
#Cello().group('start'), Cello(), Double_bass(), Double_bass().group('stop')]

#full_orchestra = [Flute().group('start'), Oboe(), Clarinet(), Bass_clarinet(),Bassoon().group('stop'), 
#French_horn().group('start'), Trombone().group('stop'), 
#Piano_RH().name('','').group('start','Piano','Pno.'),Piano_LH().name('','').group('stop'), 
#Violin().group('start'), Viola(), Cello().group('stop')]

#full_orchestra = Bassoon()

#full_orchestra = [Clarinet(), Clarinet()]

#ACO - winds 3,3,3,3; brass 4,3,3,1; harp, keyboard, timpani, 4 perc., strings 10,8,6,6,4

#winds = [Flute().name('1','1').group('start','2 Flutes','2 Fls.'),Flute().name('2','2').group('stop'),Alto_flute(),Oboe().name('1','1').group('start','2 Oboes','2 Obs.'),Oboe().name('2','2').group('stop'),English_horn(),Clarinet(),Clarinet(),
#Bass_clarinet(), Bassoon(), Bassoon(), Contrabassoon()]

#brass = [French_horn(),French_horn().clef('bass'),French_horn(),French_horn().clef('bass'),
#Trumpet(),Trumpet(),Trumpet(),Trombone(),Trombone(),Bass_Trombone(),Tuba()]

#perc_other = [Harp_RH().name('','').group('start','Harp','Harp'), Harp_LH().name('','').group('stop'), Piano_RH().name('','').group('start','Piano','Pno.'),Piano_LH().name('','').group('stop'), Vibraphone(), Timpani()]

#strings = [Violin().name('1-2','1-2').group('start','Violins I', 'Vlns I'), Violin().name('3-4','3-4'), Violin().name('5-6','5-6'), Violin().name('7-8','7-8'), Violin().name('9-10','9-10').group('stop'),
#Violin().name('1-2','1-2').group('start','Violins II', 'Vlns II'), Violin().name('3-4','3-4'), Violin().name('5-6','5-6'), Violin().name('7-8','7-8').group('stop'), 
#Viola().name('1-2','1-2').group('start','Violas','Vlas.'), Viola().name('3-4','3-4'), Viola().name('5-6','5-6').group('stop'), 
#Cello().name('1-2','1-3').group('start','Cellos','Cls.'), Cello().name('3-4','3-4'), Cello().name('5-6','5-6').group('stop'), 
#Double_bass().name('1-2','1-2').group('start','Contrabasses','Cbs.'),Double_bass().name('3-4','3-4').group('stop')]

#full_orchestra = winds+brass+perc_other+strings#experimental_group

#full_orchestra = [Bass_clarinet(), Trumpet(), Violin(), Cello(), Vibraphone(),
#Accordion(), 
#Piano_RH().name('','').group('start','Piano','Pno.'),Piano_LH().name('','').group('stop')]

full_orchestra = [Piano_RH().arbitrary_pitch_point(['C',8]),Piano_RH(),Piano_RH(),Piano_LH(),Piano_LH(),Piano_LH().arbitrary_pitch_point(['A',0])]

#full_orchestra = [Bass_clarinet().microtones(None), Guitar(), Bass_guitar(), Vibraphone_R(), Vibraphone_L()]#, Vibraphone()]

#full_orchestra = [Rhodes_RH().arbitrary_pitch_point(['C',7]),Rhodes_RH(),Rhodes_RH(),Rhodes_LH(),Rhodes_LH(),Rhodes_LH().arbitrary_pitch_point(['C',1])]

#full_orchestra = [Flute().group('start'), Clarinet().group('stop'), 
#Trumpet().group('start'), Trombone().microtones('quarter').group('stop'), Timpani().microtones('quarter'),
#Piano_RH().name('','').group('start','Piano','Pno.'),Piano_LH().name('','').group('stop'), 
#Violin().microtones('quarter').group('start'), Viola().microtones('quarter'), Cello().microtones('quarter').group('stop')]


#full_orchestra = [Violin().name('Violin IA','Vln.IA').microtones('quarter'),Violin().name('Violin IB','Vln.IB').microtones('quarter'),
#Violin().name('Violin IIA','Vln.IIA').microtones('quarter'),Violin().name('Violin IIB','Vln.IIB').microtones('quarter'),
#Viola().name('Viola IIA','Vla.IIA').microtones('quarter'),Viola().name('Viola IIB','Vla.IIB').microtones('quarter'),
#Cello().name('Cello IIA','Cel.IIA').microtones('quarter'),Cello().name('Cello IIB','Cel.IIB').microtones('quarter')]

#full_orchestra = [Soprano_saxophone()]

#full_orchestra = [Violin().name('Violin I','Vln.I').microtones('quarter'),
#Violin().name('Violin II','Vln.II').microtones('quarter'),
#Viola().name('Viola IIA','Vla.IIA').microtones('quarter'),
#Cello().name('Cello','Cel.').microtones('quarter')]

choir_weights = {'strings':3, 'winds':2,'brass':2,'harp':1,'vibes':1, 'keyboard':1, 'percussion':1}
choir_weights = {'strings':9, 'winds':7,'brass':3,'harp':2,'vibes':2, 'keyboard':2, 'percussion':1}
choir_weights = {'strings':9, 'winds':3,'brass':1,'harp':1,'vibes':1, 'keyboard':1, 'percussion':1}
equal_choir_weights = {'strings':1, 'winds':1,'brass':1,'harp':1,'vibes':1, 'keyboard':1, 'percussion':1}


class Orchestra(Score):
	
	def add(self,instrument = None):
		if instrument:
			if type(instrument) == list:
				for e in instrument:
					self._instruments.append(e)
			else:
				self._instruments.append(instrument)
		return self
		
	def __init__(self, instrument = None):
		self._instruments = []
		if instrument:
			self.add(instrument)
	
	######ELIGIBILITY
	def eligible_instruments_in_range(self, pitch):
		eligible_instruments = []
		for e in Orchestra.instruments:
			if pitch >= e._low and pitch <= e._high:
				eligible_instruments.append(e)
		return eligible_instruments
	eligible = eligible_instruments_in_range
	def not_playing_now(self, selection, (start,stop)):
		not_playing = []
		for part in selection:
			flag = 0
			if len(part.floating_infos()._floating_infos) > 0:
				for entry in part.floating_infos()._floating_infos:
					entry_start, entry_stop = entry[0]
					if start >= entry_start and start < entry_stop:###starts in the middle
						flag+=1
					if stop <= entry_stop and stop > entry_start:###ends in the middle
						flag+=1
					if start <= entry_start and stop >= entry_stop:#starts before ends after
						flag+=1
					if start < entry_stop:
						flag+=1
					if start >= entry_start and stop <= entry_stop:#starts after ends before
						flag+=1
					if start == entry_start:	##has the same start or end
						flag+=1
					if stop == entry_stop:
						flag+=1
					
					#if stop == entry_start or start == entry_stop:#<---no directly sequential notes:  could this be a feature????
					#	flag+=1
			if flag == 0:
				not_playing.append(part)
		return not_playing
		
	def range_and_available(self, pitch, (start,stop)):
		return self.not_playing_now(self.eligible_instruments_in_range(pitch),(start,stop))
			
	def choose_choir(self, available_instruments, weight_key, factor = 1):#enables choosing the choir first
		for instrument in available_instruments:
			instrument.add_weight(weight_key[instrument._choir]*factor)#KIND OF A HACK--look at for speed imprv
		example_choir_member = Chooser().add(available_instruments).choose()#
		chosen_choir = example_choir_member._choir
		self.reset_statistics()
		chosen_choir_members = []
		for instrument in available_instruments:
			if instrument._choir == chosen_choir:
				chosen_choir_members.append(instrument)
		return chosen_choir_members
	
	########Special Case -- look for min distance (timpani)
	def check_min_distance_from_last_note(self, available_instruments, (start,stop)):
		acceptable_instruments = []
		for part in available_instruments:
			if len(part.floating_infos()._floating_infos) > 0:
				part._last_note = part.floating_infos()._floating_infos[-1]
				begining, end = part._last_note[0]
				time_difference = start - end	#difference between desired time point and last note
				if part._min_distance_from_last_note <= time_difference:#IF <, NNON-CONTIGUOUS; IF <=, CONTIGUOUS ('lines')
					acceptable_instruments.append(part)
			else:
				acceptable_instruments.append(part)
		return acceptable_instruments

	def check_min_max_length(self, available_instruments, (start,stop)):
		acceptable_instruments = []
		for part in available_instruments:
			if part._min_max_length:
				length = stop-start
				if length >= part._min_max_length[0] and length <= part._min_max_length[1]:
					acceptable_instruments.append(part)
			else:
				acceptable_instruments.append(part)		
		return acceptable_instruments
		
	##########
	
	#####EQUAL Probability...
	def random_selection(self, selection = None):
		if selection and len(selection) > 0:
			return selection[random.randint(0,len(selection)-1)]
		else:
			return None
	def random_available(self, pitch, (start,stop)):
		return self.random_selection(self.range_and_available(pitch, (start,stop)))
	
	#######STATISTICAL Stuff
	def reset_statistics(self):
		for instrument in Orchestra.instruments:
			instrument.strip_weights()
		return self
	
	def choir_weights(self, available_instruments, weight_key, factor = 1):
		for instrument in available_instruments:
			instrument.add_weight(weight_key[instrument._choir]*factor)
		return self
			
	def last_note_pitch_distance_weightor(self, available_instruments, pitch_comparison, normalize = 10,
	award_absentees = 'yes'):#award absentees by giving them the highest pitch weight
		pitches = []
		for part in available_instruments:
			if len(part.floating_infos()._floating_infos) > 0:
				part._last_note = part.floating_infos()._floating_infos[-1]
				note, octave = part._last_note[1]
				#print note,octave, 'NOTE OCTAVE'
				pitch = note_and_octave_to_midi((note, octave))
				part._voice_leading_pitch_difference = abs(pitch_comparison - pitch)#part._last_note)
				pitches.append(part._voice_leading_pitch_difference)
			else:
				part._voice_leading_pitch_difference = None
		pitches.sort()
		if len(pitches) > 0:
			furthest_pitch = pitches[-1]#use greatest distance to determine floor (greatest distance will = 0 statistical weight)
			for part in available_instruments:
				if part._voice_leading_pitch_difference:
					weight = furthest_pitch - part._voice_leading_pitch_difference
					if normalize:
						weight_normalized = putil.fit(weight,furthest_pitch,0,0,normalize-1)
						part.add_weight(weight_normalized)
					else:
						part.add_weight(weight)
					#print part, weight, 'PITCH distance'
				elif award_absentees == 'yes':
					weight = furthest_pitch
					part.add_weight(weight)
		return self
	
	def last_note_time_distance_weightor(self, available_instruments, time_comparison, normalize = 10,
	award_absentees = 'yes'):#award absentees by giving them the highest time weight
		times = []
		for part in available_instruments:
			if len(part.floating_infos()._floating_infos) > 0:
				part._last_note = part.floating_infos()._floating_infos[-1]
				start, end = part._last_note[0]
				#pitch = note_and_octave_to_midi((note, octave))
				part._voice_leading_time_difference = abs(time_comparison - end)#part._last_note)
				times.append(part._voice_leading_pitch_difference)
			else:
				part._voice_leading_time_difference = None
		times.sort()
		if len(times) > 0:
			furthest_time = times[-1]
			for part in available_instruments:
				if part._voice_leading_time_difference:
					weight = part._voice_leading_time_difference#use greatest distance to determine floor (greatest distance will = 0 statistical weight)
					if normalize:
						weight_normalized = putil.fit(weight,furthest_time,0,0,normalize-1)
						part.add_weight(weight_normalized)
					else:
						part.add_weight(weight)
					#print part, weight, 'TIME DISTANCE'
				elif award_absentees == 'yes':
					weight = furthest_time
					if normalize:
						weight_normalized = normalize-1#putil.fit(furthest_time,furthest_time,0,0,normalize-1)
						part.add_weight(weight_normalized)
					else:
						part.add_weight(weight)
		return self
	
	def bulk_total_notes_weightor(self, available_instruments, normalize = 10):#weights by sheer number of notes a part contains...
		amounts = []
		for part in available_instruments:
			part._total_number_of_floats = len(part.floating_infos()._floating_infos)
			amounts.append(part._total_number_of_floats)
		amounts.sort()
		if len(amounts) > 0:
			largest_amount = amounts[-1]
			for part in available_instruments:
				weight = largest_amount - part._total_number_of_floats
				if normalize:
					weight_normalized = putil.fit(weight,largest_amount,0,0,normalize-1)
					part.add_weight(weight_normalized)
				else:
					part.add_weight(weight)
		return self
		
	def preferred_avg_weightor(self, available_instruments, pitch_comparison, normalize = 10, preferred_or_normal = 'preferred'):
		for instrument in available_instruments:
			if preferred_or_normal == 'preferred':#preferred range or absolute range
				instrument._pitch_difference = abs(pitch_comparison - instrument._preferred_average_range)
			elif preferred_or_normal == 'absolute':
				instrument._pitch_difference = abs(pitch_comparison - instrument._average_range)
			instrument._index = instrument._pitch_difference
		available_instruments.sort(general_functions.index_sort)		#sort the instruments by _pitch_difference
		largest_distance = available_instruments[-1]._pitch_difference		#this will be the greatest distance
		for instrument in available_instruments:
			weight = largest_distance - instrument._pitch_difference	#use greatest distance to determine floor (greatest distance will = 0 statistical weight)
			if normalize:
				weight_normalized = putil.fit(weight,largest_distance,0,0,normalize-1)
				instrument.add_weight(weight_normalized)
			else:
				instrument.add_weight(weight)
			#print instrument, weight, 'range average'
		return self

	def statistical_chooser(self, pitch, (start,stop)):
		available = self.range_and_available(pitch, (start,stop))
		n_available = self.check_min_distance_from_last_note(available, (start,stop))
		n_available = self.check_min_max_length(n_available, (start,stop))
		if len(n_available) > 0:
			nn_available = self.choose_choir(n_available, choir_weights)
			#self.reset_statistics()
			self.choir_weights(nn_available, equal_choir_weights)
			self.bulk_total_notes_weightor(nn_available)
			self.preferred_avg_weightor(nn_available, pitch)
			self.last_note_pitch_distance_weightor(nn_available, pitch)
			self.last_note_time_distance_weightor(nn_available, start)
			return Chooser().add(nn_available).choose()
		else:
			return None
	
	##################	
	def stitch_measures(self, time_sig = [4,4], number = None):
		for e in Orchestra.instruments:
			e.stitch_missing_measures(time_sig,number)
		return
	def ranges(self):
		return self


#how to choose instrument???
#XXX1. RANGE -- is the pitch available?
#XXX2. AVAILABLE -- is the instrument already playing?----FIXED little BUG
#XXX3. WEIGHT -- strings should play more than, say, Flute???...
#	XXX IMPLEMENTATION:  weighting system?
#	Factors:
#		1.XXXChoirs:  strings, winds, brass, piano, harp, vibes (or switcharoo)--
#		2.XXX  Mean Range or even 'Sweet Spot!?'--low piano, harp, low flute, high vibes
#			I.  range_prefered - (middle of this) -- [in_or_out, how_close_to_middle]
#			II. added "gravity" pitch (might be I. but can override) -- [how_close]
#		3.XXX When was the last time the instrument played?  how long since?  More likely if more distance (or none).  Opposite?  Maybe (dangerous)
#		4.XXX If a consecutive note is to be played, Voice Leading?
#		5.XXX How many notes does the part have already??
#		6.    Note length - Piano not suitable for long tones...
#		X7.    Microtonal Resources? - No, treat them equally
#	
#	XXX SHOULD THE MAX BE SCALED FOR EACH METHOD??? yes, probably -- i.e. 0-9??--no 1--10- (so 50 points for everything each time??)
#	MISCELANEOUS SHYTE:
#
#	1.  ?Perhaps use a channel of stereo rec. instead of summing to mono...
#	2.  Strings should probably be divisi
#	3.  Length of tones?<------LOOK HERE
#		Options:
#			1.  simply disallow based on Min,Max...works for piano, etc. with others-->danger of no instrument being able to play important tones
#			2.  Statistical weighting...
#			3.  -->some kind of 'chopping' algo.  ie. if no instrument can play long enough, chop it into multiple Planks--if this is too difficult, simply remove a tie (DUH)
#	4.  Perhaps use a logarithmic scale for pitch comparisons (Re:  Polansky Morphological Metrics)
#
#	XXX***DECIDE CHOIR Before everything else...(remove choir-ness from voice-leading and other shit-decision)
#	
#
#	Possible Added Attributes for Instruments:
#	1.  Exhaustability.  How much should the instrument Play?--good for:  brass, timpani, vibes, pno, harp, etc.
#	2.  Range Sensitivity.  Can the high notes be played soft?  Can leaps be accomplished easily?  (brass Vs. Piano Vs. Violin)
#	XXX---Clip at Preffered!!!!
#
#	INSTRUMENTAL/ORCH. Specifics:
#	1.    Bass -- lower range to preffered; strings ranges in general...might be good indication to use arbitrary 'Sweet spot'
#	2.XXX Trombones -- use eighth-tones(?) yeah
#	3.    NEW additional filtering paradigm:  Destroy.  an available instrument can be statistically 'detroyed' if certain conditions met.
#		a).  i've played too much
#		b)   available pitch set! - timpani
#	4.XXX Clarinet, Bass Clarinet:  Subset of pitch material available for quarter-tones
#
#
#BUGs to fix:
#	1.XX  Plank slicing algorithm.  maybe reverse if before 3rd beat??eh  cheap fix-->reverse if on float...(works most of the time.->
#		CHECK -- > not on 8th entry of 8th+16
#	2.xx  not_playing_now method.  fucks up sometimes obviously
#	3.XX  8th tone placement; Font
#	4.XXX Statistics have to be reset with every choice!!!
#	5.XX  enharmonic spelling algorithm -- go through notes.  find a way to determine if something is an augmented interval
#	6.XX  stupid placement shit...
#	7.    disallow microtones below ranges
#ADD:
#	XXX Master note list--for checking purposes --- USE FLOATING INFOS method
#	'WEIGHTED'-FILTER-PARTIAL THINNING or Experiment with hi-pass filters (pre-analysis)
#
#X4. MICROTONE -- which instrument is most accurate? <---do this??  maybe add weight for a more accurate pitch.?
#    TIMPANI - ideas:  find the maximum overall amplitudes of the orig.  leave part blank use timpani to double lowest pitch(es)
#

#Ãtransposition
#Ãfix dynamics redundancies
#Ãselective quarter-tones
#Ãlook-up function for placement things:  
#	Ãdynamics
#	Ã8th tone signs

#8va signs:  property:  8va(vb?) threshold
#clef changes--(bass
#maybe have an 'even' distribution algorithm?  well, recordings evolve?
#try volume envelope, even compression....maybe

#Orchestra().stitch_measures([4,4],4)
#Orchestra().output('/Users/db/Desktop/music_xml/orchest2.xml')
