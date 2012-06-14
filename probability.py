import random
#from orchestra import *
#import orchestra

class Parameter_weight:
	def __init__(self):
		self._value = 0#LIMITLESS RANGE!
	def value(self, value):
		self._value = value
		return self

class Statistic_group:
	def __init__(self, instrument):
		self._parameters = []
		self._instrument = instrument
		
		########
		self._transposition = 0
		self._range_conservative = [['C',3],['C',4]]
		self._range = [['C',1],['C',8]]
		
	def add(self,parameter = None):
		if parameter:
			if type(parameter) == list:
				for e in parameter:
					self._parameters.append(e)
			else:
				self._parameters.append(parameter)
		return self
	def count_parameters(self):
		self._number_of_parameters = len(self._parameters)
		return self
	def total_value(self):
		self._total_values = 0
		for e in self._parameters:
			self._total_values+=e._value
		return self

Bundle = Statistic_group

class Chooser:
	def __init__(self):
		self._bundles = []
	def add(self,bundle = None):
		if bundle:
			if type(bundle) == list:
				for e in bundle:
					if e.__class__ == Bundle:
						self._bundles.append(e)
					#elif e.__class__ == orchestra.Instrument:
					else:
						self._bundles.append(e._stat_bundle)
			else:
				if bundle.__class__ == Bundle:
						self._bundles.append(e)
				#elif bundle.__class__ == orchestra.Instrument:
				else:
						self._bundles.append(e._stat_bundle)
		return self
	def random(self, max = 99):
		return random.randint(0,max)
	def propagate_members(self):
		self._total_pool = []
		for bundle in self._bundles:
			self._total_pool+=bundle.total_value()._total_values*[bundle._instrument]
		return self
	def choose(self):
		return self.propagate_members()._total_pool[random.randint(0,len(self._total_pool)-1)]#WINNER@@@@@@!!!!!



class Weight_distribution:
	def __init__(self, key):
		self._key = key
	def assign(self):
		return self

#------EXAMPLE---------
#from probability import *
#from orchestra import *
#a=Parameter_weight().value(7)
#b=Parameter_weight().value(3)    
#c=Parameter_weight().value(5)
#from orchestra import *
#v=Violin()
#g1=Statistic_group(v)
#g1.add([a,b,c])
#choo=Chooser().add(g1)
#a2=Parameter_weight().value(1)
#b2=Parameter_weight().value(0)
#c2=Parameter_weight().value(2)
#c=Cello()
#g2=Statistic_group(c)
#g2.add([a2,b2,c2])
#choo.add(g2)
#choo.choose()
