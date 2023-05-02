# with stacked bar chart

import math
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import hsv_to_rgb

days = 30

def general_term(n, k):
    term = 1 / (2 * math.pi) * (math.acos((days//2 - n - k) / (days//2 - n)) - math.acos((days//2 + 1 - n - k) / (days//2 - n)))
    return term

def calculate_sequence(n):
    sequence_values = []
    for k in range(1 + n, days - n + 1):
        sequence_values.append(general_term(n, k - n))
    return sequence_values

# Calculate the sequence values for n = 0 to n = 14
all_sequence_values = [calculate_sequence(n) for n in range(days//2)]

# Define the color scheme using the HSL color space
colors = []
for i in range(days):
    hue = i / days
    saturation = 0.9
    lightness = 0.6
    colors.append(hsv_to_rgb((hue, saturation, lightness)))

# Plot the stacked bar chart
for n, sequence_values in enumerate(all_sequence_values):
    x_value = n + 1
    bottom = 0
    for k, value in enumerate(sequence_values):
        plt.bar(x_value, value, bottom=bottom, width=0.4, color=colors[k + n])
        bottom += value

# Graph title and axis labels setting
plt.title('Stacked Bar Chart of Sequence Values')
plt.xlabel('n')
plt.ylabel('Sequence Values')

# Set x-axis limits and ticks
plt.xlim(0, (days//2 + 1))
plt.xticks(range(1, (days//2 + 1)), range(days//2))

# Show the graph on the screen
plt.show()
