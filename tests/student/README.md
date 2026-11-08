# Your own tests

This directory contains `own_tests.jsonl` with 18 custom request fixtures testing boundary conditions, witnesses, hash collisions, and state resets across all eight commands (`lcs`, `merge`, `tree`, `naive`, `kmp`, `rk`, `suffix`, `aho`).

## Run Command

```sh
python3 tools/run.py --input tests/student/own_tests.jsonl