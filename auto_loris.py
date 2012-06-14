#!usr/bin/python
import loris, string, partial_sorter, math, sys, os, commands, general_functions


def analyze_aiff(path, resolution_hz = 5):
	sound_file = loris.AiffFile(path)
	sound_file_vectors = sound_file.samples()
	sound_file_sample_rate = sound_file.sampleRate()
	analysis_instance = loris.Analyzer(resolution_hz)
	analysis_data = analysis_instance.analyze(sound_file_vectors,sound_file_sample_rate)
	return analysis_data



def get_length_of_aiff(aiff_file):
	sound_file = loris.AiffFile(aiff_file)
	number_of_samples = sound_file.sampleFrames()
	sample_rate = sound_file.sampleRate()
	time_in_seconds = number_of_samples/sample_rate
	print 'file is '+str(time_in_seconds)+' seconds'
	return time_in_seconds,sample_rate
	
def simple_morph((first_aiff, second_aiff),(naked_start,naked_end)):
	first_analysis = analyze_aiff(first_aiff)
	second_analysis = analyze_aiff(second_aiff)
	
	length_of_first = get_length_of_aiff(first_aiff)[0]
	length_of_second = get_length_of_aiff(second_aiff)[0]
	longest = max(length_of_first,length_of_second)
	
	if longest == length_of_first:
		loris.dilate(second_analysis,[0.,length_of_second],[0,length_of_first])
	elif longest == length_of_second:
		loris.dilate(first_analysis,[0.,length_of_first],[0,length_of_second])
	#loris.distill(first_analysis)
	#loris.distill(second_analysis)
	envelope_create = loris.BreakpointEnvelope()
	envelope_create.insertBreakpoint(naked_start,0)
	envelope_create.insertBreakpoint(longest-naked_end,1)
	morph = loris.morph(first_analysis,second_analysis,envelope_create,envelope_create, envelope_create)
	loris.crop(morph,0,longest)
	synth = loris.synthesize(morph, 44100)
	loris.exportAiff( first_aiff+'morph.aiff',synth,44100, 1, 16 )

def thin_by_duration(partialList,minimum_duration):#stolen---
	iter = partialList.begin()
	end = partialList.end()
	tempList = loris.PartialList()
	tempIter = tempList.begin()
	while not iter.equals(end):
		part = iter.partial()
		dur = part.duration()
		if dur >= minimum_duration:
			tempIter = tempList.insert(tempIter, part)
			tempIter = tempIter.next()
			#print tempIter
		iter = iter.next()
	print tempList.size(),'partials'
	return tempList
def get_amplitude_thinning_residue(partialList,minimum_amplitude):
	global amplitudes_master_list
	iter = partialList.begin()
	end = partialList.end()
	average_amplitudes = []
	while not iter.equals(end):
		part = iter.partial()
		partIter = part.begin()
		partIterEnd = part.end()
		number_of_breakpoints = part.numBreakpoints()
		amp = 0
		while not partIter.equals(partIterEnd):
			time = partIter.time()
			bp = partIter.breakpoint()
			frequency,amplitude,phase = bp.frequency(), bp.amplitude(),bp.phase()
			#print time,frequency,amplitude,phase
			#amplitude = amp + pow(bp.amplitude(), 2)
			partIter = partIter.next()
		average_amplitudes.append(amplitude/number_of_breakpoints)
		iter = iter.next()
	iter = partialList.begin()
	end = partialList.end()
	tempList = loris.PartialList()
	tempIter = tempList.begin()
	peak = max(average_amplitudes)
	cutoff = minimum_amplitude*peak
	i = 0
	while not iter.equals(end):
		part = iter.partial()
		#print part.initialPhase()
		if average_amplitudes[i] <= cutoff:
			amplitudes_master_list.append(average_amplitudes[i])
			tempIter = tempList.insert(tempIter, part)
			tempIter = tempIter.next()
		i += 1
		iter = iter.next()
	print tempList.size(),'partials'
	return tempList
amplitudes_master_list = []
def thin_by_amplitude(partialList,minimum_amplitude):#stolen
	global amplitudes_master_list
	iter = partialList.begin()
	end = partialList.end()
	average_amplitudes = []
	while not iter.equals(end):
		part = iter.partial()
		partIter = part.begin()
		partIterEnd = part.end()
		number_of_breakpoints = part.numBreakpoints()
		amp = 0
		while not partIter.equals(partIterEnd):
			time = partIter.time()
			bp = partIter.breakpoint()
			frequency,amplitude,phase = bp.frequency(), bp.amplitude(),bp.phase()
			#print time,frequency,amplitude,phase
			#amplitude = amp + pow(bp.amplitude(), 2)
			partIter = partIter.next()
		average_amplitudes.append(amplitude/number_of_breakpoints)
		iter = iter.next()
	iter = partialList.begin()
	end = partialList.end()
	tempList = loris.PartialList()
	tempIter = tempList.begin()
	peak = max(average_amplitudes)
	cutoff = minimum_amplitude*peak
	i = 0
	while not iter.equals(end):
		part = iter.partial()
		#print part.initialPhase()
		if general_functions.amplitude_to_dB(average_amplitudes[i]) >= cutoff:
			amplitudes_master_list.append(average_amplitudes[i])
			tempIter = tempList.insert(tempIter, part)
			tempIter = tempIter.next()
		i += 1
		iter = iter.next()
	print tempList.size(),'partials'
	return tempList

rmsMasterList = []
masterNameList = []	

def thin_by_rms_amplitude(partialList,minimum_amplitude):#stolen
	global rmsMasterList
	iter = partialList.begin()
	end = partialList.end()
	rmsAmps = []
	while not iter.equals(end):
		part = iter.partial()
		partIter = part.begin()
		partIterEnd = part.end()
		numBP = part.numBreakpoints()
		amp = 0
		while not partIter.equals(partIterEnd):
			time = partIter.time()
			bp = partIter.breakpoint()
			frequency,amplitude,phase = bp.frequency(), bp.amplitude(),bp.phase()
			#print time,frequency,amplitude,phase
			amp = amp + pow(bp.amplitude(), 2)
			partIter = partIter.next()
		rmsAmps.append(math.sqrt(amp / numBP))
		iter = iter.next()
	iter = partialList.begin()
	end = partialList.end()
	tempList = loris.PartialList()
	tempIter = tempList.begin()
	peak = max(rmsAmps)
	cutoff = minimum_amplitude*peak
	i = 0
	while not iter.equals(end):
		part = iter.partial()
		#print part.initialPhase()
		if rmsAmps[i] >= cutoff:
			rmsMasterList.append(rmsAmps[i])
			tempIter = tempList.insert(tempIter, part)
			tempIter = tempIter.next()
		i += 1
		iter = iter.next()
	print tempList.size(),'partials'
	return tempList
	
def thin_by_duration_and_amplitude(partialList,minimum_duration,minimum_amplitude):
	long_partials = thin_by_duration(partialList,minimum_duration)
	loud_long_partials = thin_by_rms_amplitude(long_partials,minimum_amplitude)
	return loud_long_partials

	
	
	
def get_lists_from_sdif(partialList):#busted------------
	iter = partialList.begin()
	partial_list_end = iter.end
	while not iter.equals(partial_list_end):
		partial = iterator.partial()
		partial_end = partial.end()
		while not partial.equals(partial_end):
			breakpoint = partial.breakpoint()
			breakpoint_end = breakpoint.end()
			while not breakpoint.equals(breakpoint_end):
				print breakpoint.amplitude()
				breakpoint = breakpoint.next()
			partial = partial.next()
		iter = iter.next()

def get_list_from_partial_list(partialList):
	#global rmsMasterList
	iter = partialList.begin()
	end = partialList.end()
	#rmsAmps = []
	master_list = []
	partial_number = 0
	while not iter.equals(end):
		part = iter.partial()
		partIter = part.begin()
		partIterEnd = part.end()
		numBP = part.numBreakpoints()
		partial_list = []
		#amp = 0
		while not partIter.equals(partIterEnd):
			bp = partIter.breakpoint()
			time = partIter.time()
			frequency,amplitude,phase = bp.frequency(), bp.amplitude(),bp.phase()
			element = [partial_number,time,frequency,amplitude,phase]
			#amp = amp + pow(bp.amplitude(), 2)
			partial_list.append(element)
			partIter = partIter.next()
		#rmsAmps.append(math.sqrt(amp / numBP))
		master_list.append(partial_list)
		partial_number+=1
		iter = iter.next()
	return master_list

def resynthesize(partials,path, samplerate = 44100, nchannels = 1, bitsPerSamp = 16):
	resynthesis_vector = loris.synthesize(partials,samplerate)
	loris.exportAiff(path,resynthesis_vector,samplerate,nchannels,bitsPerSamp)

spew_sdif_path = '/print/Spatial_Notation_Machine/'
def spew_sdif_from_file(sdif_file,spew_sdif_path='/print/Spatial_Notation_Machine/'):
	commands.getstatusoutput(spew_sdif_path+'spew-sdif '+sdif_file)

#if len(sys.argv) != 5:
#	print 'ERROR: params--aiff_file, minimum_duration, minimum amplitude, resampling_interval'
#	sys.exit(1)

resampled_sdif = 0

#aiff_file = str(sys.argv[1])
#minimum_duration = float(sys.argv[2])
#minimum_amplitude = float(sys.argv[3])
#resampling_interval = float(sys.argv[4])
#make resynthesis and other file output flags...

class Loris_set:
	def analyze(self, aiff_file=None, resolution_hz = 5.0):
		aiff_file = aiff_file or self.aiff_file
		self.analysis = analyze_aiff(self.aiff_file)#, resolution_hz)
		self.original_partials = self.analysis#store a copy of the original analysis data
		loris.exportSdif(aiff_file[:-4]+'.sdif', self.analysis)
	def analyze_if_needed(self, aiff_file = None):
		if aiff_file and os.path.isfile(aiff_file[:-4]+'.sdif'):#is there a twin sdif analysis
			self.analysis = loris.importSdif(aiff_file[:-4]+'.sdif')#if so, use it
		else:
			self.analyze(aiff_file)
		return self
	def __init__(self, aiff_file = None):
		self.aiff_file = aiff_file
		self.minimum_duration,self.minimum_amplitude,self.resampling_interval = .5,.5,.5
		self.analysis_data = []
		self.original_partials = []
		self.partials = []
		self.partials_list = []
		#self.analyze(self, aiff_file)
	def set_params(self, minimum_duration = None, minimum_amplitude = None, resampling_interval = None):
		self.minimum_duration,self.minimum_amplitude,self.resampling_interval = minimum_duration, minimum_amplitude, resampling_interval
		return self
	def thin(self, minimum_duration = None, minimum_amplitude = None):
		minimum_duration = minimum_duration or self.minimum_duration
		minimum_amplitude = minimum_amplitude or self.minimum_amplitude
		self.analysis = thin_by_duration_and_amplitude(self.analysis, minimum_duration, minimum_amplitude)
		return self
	def resample(self, resampling_interval = None):
		resampling_interval = resampling_interval or self.resampling_interval
		loris.resample(self.analysis,resampling_interval)
		return self
	def make_list(self):
		self.partials_list = get_list_from_partial_list(self.analysis)
		return self.partials_list
	def get_time_chunks(self):
		return partial_sorter.total_sort_sdif(self.make_list(),self.resampling_interval)
	def resynthesize(self, path):
		resynthesize(self.analysis, path)
		return self

def do_sort(aiff_file,minimum_duration,minimum_amplitude,resampling_interval):
	analysis_data = analyze_aiff(aiff_file)
	thinned_data = thin_by_duration_and_amplitude(analysis_data,minimum_duration,minimum_amplitude)
	#loris.exportSdif(aiff_file[0:-4]+'-thinned.sdif',thinned_data)
	loris.resample(thinned_data,resampling_interval)
	#resynthesize(thinned_data,aiff_file[0:-4]+'-resynth.aiff')
	unthinned_list = get_list_from_partial_list(analysis_data)
	master_list = get_list_from_partial_list(thinned_data)
	thinned_list = master_list
	#print master_list
	#----residue
	#residue_partials = get_amplitude_thinning_residue(analysis_data,minimum_amplitude)
	#resynthesize(residue_partials,aiff_file[0:-4]+'residue.wav')
	#-----
	#unindent and de-comment for 'partials files' to be written
	partials_file = open(aiff_file[0:-4]+'-.partials', 'w')
	partials_file.write(str(master_list))
	print 'Partials file written at <'+aiff_file+'-.partials>'
	sorted_master = partial_sorter.total_sort_sdif(master_list,resampling_interval)#organizes by time as opposed to partials
	return sorted_master, (unthinned_list, thinned_list)

	
	
	
	
