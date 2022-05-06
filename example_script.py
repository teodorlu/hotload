#!/usr/bin/env python3

import random

print("Running example_script")

assert random.random() < 0.9, "Bad luck!"

def test():
    print("Running example_script.test")
    return 123

print("done with example_script")
