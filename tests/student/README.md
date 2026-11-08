# Student Test Suite

`tests/student/own_tests.jsonl` contains 18 custom JSONL requests covering empty inputs, subsequence vs. substring behaviour, adjacent-only block merging vs. greedy non-adjacent traps, deep chain and 64-bit weight trees, punctuation/overlap consistency across `naive`/`kmp`/`rk`, base-31 mod-101 collisions (`ab`/`dj` and `bc`/`ek`), distinct/overlapping suffix arrays, and Aho–Corasick suffix links, duplicates, and state resets. Run with:

```sh
python3 tools/run.py --input tests/student/own_tests.jsonl