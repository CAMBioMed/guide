#!/usr/bin/env python3

# Usage:
#     python3 check_labels.py labelset.csv labelsettext.csv

import csv
import sys


def read_csv(filename):
    entries = {}

    with open(filename, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)

        required = {"Label ID", "Short Code"}
        missing = required - set(reader.fieldnames or [])
        if missing:
            sys.exit(
                f"{filename}: missing required column(s): "
                f"{', '.join(sorted(missing))}"
            )

        for rownum, row in enumerate(reader, start=2):
            label_id = row["Label ID"].strip()
            short_code = row["Short Code"].strip()

            if not label_id:
                continue

            entries.setdefault(label_id, set()).add(short_code)

    return entries


def main():
    if len(sys.argv) != 3:
        sys.exit(f"Usage: {sys.argv[0]} EXPECTED.csv FULL.csv")

    expected = read_csv(sys.argv[1])
    full = read_csv(sys.argv[2])

    problems = False

    #
    # Check everything expected is present and correct.
    #

    missing_ids = []
    wrong_codes = []

    for label_id, expected_codes in expected.items():
        if label_id not in full:
            for code in sorted(expected_codes):
                missing_ids.append((label_id, code))
            continue

        missing_codes = expected_codes - full[label_id]

        if missing_codes:
            wrong_codes.append(
                (
                    label_id,
                    sorted(expected_codes),
                    sorted(full[label_id]),
                )
            )

    #
    # Check for things in the full CSV that aren't in expected.csv.
    #

    extra_ids = []
    extra_pairs = []

    for label_id, full_codes in full.items():

        # Entire Label ID is unknown
        if label_id not in expected:
            for code in sorted(full_codes):
                extra_ids.append((label_id, code))
            continue

        # Label ID exists, but full CSV has additional unexpected codes
        unexpected_codes = full_codes - expected[label_id]

        for code in sorted(unexpected_codes):
            extra_pairs.append((label_id, code))

    #
    # Report
    #

    if missing_ids:
        problems = True
        print("Missing from full CSV:")
        for label_id, code in missing_ids:
            print(f"  {label_id},{code}")
        print()

    if wrong_codes:
        problems = True
        print("Label IDs with wrong Short Code:")
        for label_id, expected_codes, found_codes in wrong_codes:
            print(
                f"  Label ID {label_id}: "
                f"expected {', '.join(repr(x) for x in expected_codes)}, "
                f"found {', '.join(repr(x) for x in found_codes)}"
            )
        print()

    if extra_ids:
        problems = True
        print("Extra Label IDs in full CSV:")
        for label_id, code in extra_ids:
            print(f"  {label_id},{code}")
        print()

    if extra_pairs:
        problems = True
        print("Unexpected Short Codes for known Label IDs in full CSV:")
        for label_id, code in extra_pairs:
            print(f"  {label_id},{code}")
        print()

    if not problems:
        print("OK: Label IDs and Short Codes match exactly.")
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())