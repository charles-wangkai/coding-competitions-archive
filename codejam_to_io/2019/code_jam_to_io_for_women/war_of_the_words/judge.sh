#!/bin/bash

for test_number in 0 1; do
  echo Testing with test_number $test_number ...
  python3 interactive_runner.py python codejam_to_io/2019/code_jam_to_io_for_women/war_of_the_words/output_validators/validator/judge.py $test_number -- java "$1"
done