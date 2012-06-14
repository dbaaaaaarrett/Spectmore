import math

def clamp(value, min_value, max_value):
    'Keep the value within the range of min_value to max_value.'
    if value < min_value:
        return min_value
    elif value > max_value:
        return max_value
    else:
        return value

def fit(value, old_min, old_max, new_min, new_max, do_clamp = 1):
    '''Return a new number that has the same proportional relationship
to new_min and new_max as it does to old_min and old_max.
For example, fit(3, 0, 10, 0, 100) => 30'''
    if old_max == 0:
	    old_max = .0000000001
    new_value = new_min + \
		       ((value - old_min) / (float(old_max) - old_min)) * \
		       (new_max - new_min)
    if do_clamp:
		new_value = clamp(new_value, new_min, new_max)
    return new_value

def dist(x1, y1, x2, y2):
    'Return the distance between point [x1,y1] and point [x2,y2].'
    dx = x2 - x1
    dy = y2 - y1
    return math.sqrt(dx * dx + dy * dy)

def rgb(r, g, b):
    'Create PIL color specifier. Channels r, g, b are from 0.0 to 1.0.'
    return 'rgb(%d%%,%d%%,%d%%)' % (r*100, g*100, b*100)

def rgb8(r, g, b):
    'Create PIL color specifier. Channels r, g, b are from 0 to 255.'
    return 'rgb(%d,%d,%d)' % (r, g, b)
