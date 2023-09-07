#!/bin/bash

for test_number in 0 1; do
  echo Testing with test_number $test_number ...
  python3 interactive_runner.py python kickstart/2019/practice_round/number_guessing/output_validators/validator/judge.py $test_number -- java "$1"
done