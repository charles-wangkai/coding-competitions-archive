import base64
import json
import os
from pathlib import Path
import pprint
import requests
import subprocess
import sys
import tempfile
import time


def find_validator_launcher(validator_file):
    if validator_file.endswith(".py"):
        return "python"
    if validator_file.endswith(".py3"):
        return "python3"
    if validator_file.endswith(".java"):
        return "java"


def get_limit(problem_limits, input_file, key):
    if key in problem_limits:
        return problem_limits[key]

    for test_set in problem_limits:
        if test_set in input_file:
            return problem_limits[test_set][key]

    raise RuntimeError


def main(problem_folder, submission_file):
    print("problem_folder:", problem_folder)
    print("submission_file:", submission_file)

    problem_limits = json.loads(
        Path(os.path.join(problem_folder, "judge0.json")).read_text()
    )
    print("problem_limits:")
    print(json.dumps(problem_limits, indent=4))

    for dirpath, _, filenames in os.walk(problem_folder):
        for filename in filenames:
            if filename == "1.in.part00":
                print(f"Concating file: {dirpath}/1.in")

                concat_result = subprocess.run(
                    f"cat {dirpath}/1.in.part* > {dirpath}/1.in", shell=True
                )
                if concat_result.returncode:
                    print("Internal Error - Input file concat failed!")

                    break

    input_files = []
    validator_file = None
    for dirpath, _, filenames in os.walk(problem_folder):
        for filename in filenames:
            if filename.endswith(".in"):
                input_files.append(os.path.join(dirpath, filename))
            elif "output_validators" in dirpath:
                validator_file = os.path.join(dirpath, filename)

    input_files.sort()
    print("input_files:")
    pprint.pprint(input_files, width=-1)

    print("validator_file:", validator_file)

    for input_file in input_files:
        print()
        print("=" * 10, "Checking", input_file, "=" * 10)

        answer_file = input_file[: -len(".in")] + ".ans"

        while True:
            try:
                r = requests.post(
                    "http://localhost:2358/submissions?base64_encoded=true",
                    data={
                        "language_id": 62,
                        "source_code": base64.b64encode(
                            Path(submission_file).read_bytes()
                        ).decode(),
                        "stdin": base64.b64encode(
                            Path(input_file).read_bytes()
                        ).decode(),
                        "expected_output": None
                        if validator_file
                        else base64.b64encode(Path(answer_file).read_bytes()).decode(),
                        "cpu_time_limit": get_limit(
                            problem_limits, input_file, "cpu_time_limit"
                        ),
                        "memory_limit": get_limit(
                            problem_limits, input_file, "memory_limit"
                        ),
                    },
                )
                r.raise_for_status()
                resp = r.json()
                submission_token = resp["token"]
                print("submission_token:", submission_token)

                break
            except Exception as e:
                print(e)

                time.sleep(5)

        while True:
            try:
                r = requests.get(
                    f"http://localhost:2358/submissions/{submission_token}"
                )
                r.raise_for_status()
                resp = r.json()
                if resp["status"]["description"] not in ["In Queue", "Processing"]:
                    break
            except Exception as e:
                print(e)

            time.sleep(1)

        print("submission:")
        print(json.dumps({k: resp[k] for k in resp if k != "stdout"}, indent=4))
        if resp["status"]["description"] != "Accepted":
            break

        if validator_file:
            output_file = tempfile.NamedTemporaryFile(delete=False)
            Path(output_file.name).write_text(resp["stdout"])

            if validator_file.endswith(".cc"):
                compilation_result = subprocess.run(
                    ["g++", "-std=c++11", "-w", validator_file]
                )
                if compilation_result.returncode:
                    print("Internal Error - Validator compilation failed!")

                    break

                validation_result = subprocess.run(
                    ["./a.out", input_file, output_file.name, answer_file]
                )
            else:
                validation_result = subprocess.run(
                    [
                        find_validator_launcher(validator_file),
                        validator_file,
                        input_file,
                        output_file.name,
                        answer_file,
                    ]
                )

            if validation_result.returncode:
                print("Wrong Answer - Validation failed!")

                break
            else:
                print("Accepted - Validation passed!")


if __name__ == "__main__":
    problem_folder = sys.argv[1]
    submission_file = sys.argv[2]

    main(problem_folder, submission_file)
