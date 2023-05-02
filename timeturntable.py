import numpy as np
import librosa
import matplotlib.pyplot as plt
import math
import soundfile as sf

# n 값 설정
n = 15

# 수열 정의
def sequence(n):
    result = []
    for k in range(1, 2*n + 1):
    # for k in range(1, n+1):
        ak = (math.acos((n - k) / n) - math.acos((n - k + 1) / n)) / (math.pi/2)
        print(n, k, ak)
        print(math.acos((n - k) / n))
        result.append(ak)
    return result

# # Define the frequencies in a logarithmic scale
# frequencies = np.logspace(np.log10(20), np.log10(2000), n)

# # Generate the audio for each a_k and f_k
# y = sequence(n)
# sample_rate = 44100
# duration = 1

# # Create an empty array to store the audio samples
# audio_samples = np.array([])

# for i, a_k in enumerate(y):
#     f_k = frequencies[i]
#     t = np.linspace(0, duration, duration * sample_rate, False)
#     audio = np.sin(f_k * 2 * np.pi * t) * a_k
#     audio_samples = np.concatenate((audio_samples, audio))

# # Save the audio as a WAV file
# # librosa.output.write_wav('output_audio.wav', audio_samples, sample_rate)
# sf.write('output_audio.wav', audio_samples, sample_rate)

# 그래프를 그리기 위한 x, y 좌표 생성
x = list(range(1, 2*n + 1))
y = sequence(n)



# 그래프 그리기
plt.plot(x, y, marker='o', linestyle='-', label='수열')

# 그래프 제목 및 축 레이블 설정
plt.title('a_k = arccos(k/n) - arccos((k-1)/n) 그래프 (n=100)')
plt.xlabel('k')
plt.ylabel('a_k')

# 범례 표시
plt.legend()

# 그래프를 화면에 표시
plt.show()

# Plotting the stacked bar chart
bottom = 0
for idx, value in enumerate(y):
    plt.bar(x[idx], value, bottom=bottom, width=0.4)
    bottom += value

# Graph title and axis labels setting
plt.title('Stacked Bar Chart of a_k = arccos(k/n) - arccos((k-1)/n) (n=100)')
plt.xlabel('k')
plt.ylabel('a_k')

# Show the graph on the screen
plt.show()

# Plotting the stacked bar chart
x_value = 1
bottom = 0
for value in y:
    plt.bar(x_value, value, bottom=bottom, width=0.4)
    bottom += value

# Graph title and axis labels setting
plt.title('Stacked Bar Chart of a_k = arccos(k/n) - arccos((k-1)/n) (n=100)')
plt.xlabel('x')
plt.ylabel('a_k')

# Set x-axis limits and ticks
plt.xlim(0, 2)
plt.xticks([x_value], ['Stacked Bars'])

# Show the graph on the screen
plt.show()