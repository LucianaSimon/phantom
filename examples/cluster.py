# pylint: disable=E0001
# pylint: disable=E1101

import cv2
import sys
import datetime
import dlib
import glob
import numpy as np
import os


from concurrent.futures import ProcessPoolExecutor
from phantom.faces import detect, encode
from pprint import pprint


path  = r"D:\Storage-post-SSD\gender\test\small"
procs = 3
DEBUG_TIMER = True
output_folder_path = r"D:\Storage-post-SSD\gender\test\small_clustered"


def read_and_find(path):
    print(f"Reading {path}...")
    img = cv2.imread(path)
    if img is None:
        return []
    locations = detect(img)
    if not(locations):
        return []
    return img, encode(img, locations=locations)


def main():
    t0 = datetime.datetime.now()
    with ProcessPoolExecutor(max_workers=procs) as executor:
        futures = []
        for filename in glob.glob(os.path.join(path, "*.jpg")):
            futures.append(executor.submit(read_and_find, filename))
    results = []
    for f in futures:
        result = f.result()
        if result:
            results.append(result)
    # now we have to process the faces...
    t1 = datetime.datetime.now()

    images = [r[0] for r in results]
    results = [dlib.vector(r[1][0]) for r in results]  # tied to 1 face per image...
    labels = dlib.chinese_whispers_clustering(results, 0.5)
    num_classes = len(set(labels))

    t2 = datetime.datetime.now()
    
    print("Number of clusters: {}".format(num_classes))
    print("Saving faces to output folder...")

    for i, label in enumerate(labels):
        img = images[i]
        file_path = os.path.join(output_folder_path, f"{label}_face_{i}.jpg")
        cv2.imwrite(file_path, img)

    if DEBUG_TIMER:
        print(f"Time taken encoding  : {t1 - t0}")
        print(f"Tome taken clustering: {t2 - t1}")
        print(f"Total time           : {t2 - t0}")

if __name__ == "__main__":
    main()