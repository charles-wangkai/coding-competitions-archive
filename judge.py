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


def main(problem_folder, submission_file):
    print("problem_folder:", problem_folder)
    print("submission_file:", submission_file)

    problem_limits = json.loads(
        Path(os.path.join(problem_folder, "judge0.json")).read_text()
    )
    print("problem_limits:", problem_limits)

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

        r = requests.post(
            "http://localhost:2358/submissions?base64_encoded=true",
            data={
                "language_id": 62,
                "source_code": base64.b64encode(
                    Path(submission_file).read_bytes()
                ).decode(),
                "stdin": base64.b64encode(Path(input_file).read_bytes()).decode(),
                "expected_output": None
                if validator_file
                else base64.b64encode(Path(answer_file).read_bytes()).decode(),
                "cpu_time_limit": problem_limits["cpu_time_limit"],
                "memory_limit": problem_limits["memory_limit"],
            },
        )
        r.raise_for_status()
        resp = r.json()
        submission_token = resp["token"]
        print("submission_token:", submission_token)

        while True:
            r = requests.get(f"http://localhost:2358/submissions/{submission_token}")
            r.raise_for_status()
            resp = r.json()
            if resp["status"]["description"] not in ["In Queue", "Processing"]:
                break

            time.sleep(1)

        print("submission:")
        print(json.dumps({k: resp[k] for k in resp if k != "stdout"}, indent=4))
        if resp["status"]["description"] != "Accepted":
            break

        if validator_file:
            output_file = tempfile.NamedTemporaryFile(delete=False)
            Path(output_file.name).write_text(resp["stdout"])

            validation_result = subprocess.run(
                [
                    "python3" if validator_file.endswith(".py3") else "python",
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
