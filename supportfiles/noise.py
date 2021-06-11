import numpy as np
import random
from PIL import Image

"""
add the noise lines, takes 1 parameter draw which is d when using it
1st & second for loops >> add lines, 2 of them so theyre positioned differently
"""
def add_noise_lines(draw):
    size = (305, 95)

    for _ in range(1):
        width = random.choice((1, 2))
        start = (0, random.randint(0, size[1] - 1))
        end = (size[0], random.randint(0, size[1] - 1))
        draw.line([start, end], fill="white", width=width)

    for _ in range(1):
        start = (-50, -50)
        end = (size[0] + 10, random.randint(0, size[1] + 10))
        draw.arc(start + end, 0, 360, fill="white")
    return draw

"""
add the salt and pepper effect to our images using numpy
"""
def salt_and_pepper(image, prob):
    arr = np.asarray(image)
    original_dtype = arr.dtype
    intensity_levels = 2 ** (arr[0, 0].nbytes * 8)
    min_intensity = 0
    max_intensity = intensity_levels - 1
    random_image_arr = np.random.choice(
        [min_intensity, 1, np.nan], p=[prob / 2, 1 - prob, prob / 2], size=arr.shape
    )
    salt_and_peppered_arr = arr.astype(np.float_) * random_image_arr
    salt_and_peppered_arr = np.nan_to_num(
        salt_and_peppered_arr, nan=max_intensity
    ).astype(original_dtype)

    return Image.fromarray(salt_and_peppered_arr)
