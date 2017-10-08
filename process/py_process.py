from math import sqrt

DIMENSION = 255
DEFUALT_EPSILON = 2.0

def __decode_input(line):
  result = []
  x_low = y_low = float('inf')
  x_high = y_high = 0
  for stroke in line.split('-'):
    if stroke:
      result.append([[], []])
      for i, coordinate in enumerate(stroke.split('|')):
        coordinate = int(coordinate)
        result[-1][i & 1].append(coordinate)
        if i & 1: y_low, y_high = min(coordinate, y_low), max(coordinate, y_high)
        else: x_low, x_high = min(coordinate, x_low), max(coordinate, x_high)
  return result, x_low, x_high, y_low, y_high

def __normalize(strokes, x_low, x_high, y_low, y_high):
  # Find boundaries
  current_dimension = 1 + max(x_high - x_low, y_high - y_low)
  
  # Align to upper-left, and stretch to dimension
  for stroke in strokes:
    x, y = stroke
    x[:] = [(v - x_low) * DIMENSION / current_dimension for v in x]
    y[:] = [(v - y_low) * DIMENSION / current_dimension for v in y]

def __perpendicular_distance(point, start, end):
  x, y = (v - n for v, n in zip(point, start))
  b, a = (v - n for v, n in zip(end, start))
  return abs(a * x - b * y) / sqrt(a * a + b * b)

# Ramer-Douglas-Peucker Line Simplification
def __RDP(curve_list, epsilon):
  def single(curve):
    curve = zip(*curve)
    def helper(i, j):
      pivot = max_distance = 0
      start, end = curve[i], curve[j - 1]
      for x in xrange(i, j):
        p = curve[x]
        d = __perpendicular_distance(p, start, end)
        if d > max_distance:
          pivot, max_distance = x, d
      if max_distance <= epsilon:
        return [start, end]
      result = helper(i, pivot + 1)
      tail = helper(pivot, j)
      tail.pop(0)
      result.extend(tail)
      return result
    return [list(x) for x in zip(*helper(0, len(curve)))]
  return [single(curve) for curve in curve_list]

def parse_input(text, normalize=False, RDP=False, epsilon=DEFUALT_EPSILON):
  result, x_low, x_high, y_low, y_high= __decode_input(text)
  if normalize:
    __normalize(result, x_low, x_high, y_low, y_high)
  if RDP:
    result = __RDP(result, epsilon)
  return result
