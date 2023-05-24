import math

def general_term(n, k):
    term = 1 / (2 * math.pi) * (math.acos((16 - n - k - 1) / (15 - n)) - math.acos((16 - n - k) / (15 - n)))
    return term

n = int(input("Enter the value of n: "))
# k = int(input("Enter the value of k: "))
k = 0
# Calculate the first two general terms of the sequence
a_1 = general_term(n, 1)
a_2 = general_term(n, 2)
# a_k = general_term(n, k)
# Calculate the ratio of the first two general terms
ratio = a_1 / a_2

# Print the result
print(f"The ratio of the first two general terms of the sequence is: {ratio}")
for k in range(1, 30-2*n+1):
    print(f"a_", k, ":", general_term(n, k))
for k in range(1, 30-2*n):    
    print(f"ratio",":", general_term(n, k)/general_term(n, k+1))
