if p <= 0.1:
    bin_idx = 0
else:
    bin_idx = int(math.ceil(p * 10)) - 1
