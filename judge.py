import base64
import json
import os
from pathlib import Path
import pprint
import requests
import sys
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
    for dirpath, dirnames, filenames in os.walk(problem_folder):
        for filename in filenames:
            if filename.endswith(".in"):
                input_files.append(os.path.join(dirpath, filename))
            elif "output_validators" in dirpath:
                validator_file = os.path.join(dirpath, filename)

    input_files.sort()
    print("input_files:")
    pprint.pprint(input_files, width=-1)

    print("validator_file:", validator_file)
    if validator_file:
        raise NotImplementedError

    for input_file in input_files:
        print()
        print("=" * 10, "Checking", input_file, "=" * 10)

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
                else base64.b64encode(
                    Path(input_file[: -len(".in")] + ".ans").read_bytes()
                ).decode(),
                "cpu_time_limit": problem_limits["cpu_time_limit"],
                "memory_limit": problem_limits["memory_limit"],
            },
        )
        r.raise_for_status()
        resp = r.json()
        submission_token = resp["token"]
        print("submission_token:", submission_token)

        while True:
            r = requests.get(
                f"http://localhost:2358/submissions/{submission_token}?fields=time,memory,stderr,compile_output,message,status"
            )
            r.raise_for_status()
            resp = r.json()
            if resp["status"]["description"] not in ["In Queue", "Processing"]:
                break

            time.sleep(1)

        print("submission:")
        print(json.dumps(resp, indent=4))
        if resp["status"]["description"] != "Accepted":
            break


if __name__ == "__main__":
    problem_folder = sys.argv[1]
    submission_file = sys.argv[2]

    main(problem_folder, submission_file)
