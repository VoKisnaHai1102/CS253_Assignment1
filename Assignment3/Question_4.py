import numpy as np

def apply_filter(image, kernel):
    h, w = image.shape
    padded = np.pad(image, pad_width=1, mode='constant', constant_values=0) # first padding with zeroes for convulsion
    output = np.zeros((h, w), dtype=np.float64) # output array to store the results of convolution
    for i in range(h):
        for j in range(w):
            region = padded[i : i+3, j : j+3] # extracting the 3x3 region of the padded image corresponding to the current pixel
            output[i, j] = np.sum(region * kernel)
    output = np.clip(output, 0, 255).astype(np.int32) # clipping the output values to be in the range [0, 255] and converting to integer type
    return output

# put your input here

dummy_img = np.array([
    [10, 10, 10],
    [10, 50, 10],
    [10, 10, 10]
])

edge_kernel = np.array([
    [-1, -1, -1],
    [-1,  8, -1],
    [-1, -1, -1]
])

print(apply_filter(dummy_img, edge_kernel))