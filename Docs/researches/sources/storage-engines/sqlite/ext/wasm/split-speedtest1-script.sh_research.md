# sources/storage-engines/sqlite/ext/wasm/split-speedtest1-script.sh

## Purpose
`split-speedtest1-script.sh` converts a single `speedtest1 --script` SQL output file into one SQL file per test block. It is a developer utility for inspecting or replaying individual speedtest1 tests.

## Important APIs, Types, And Functions
The script is a compact Bash pipeline. It requires one positional argument, extracts test numbers with `grep -e '^-- begin test'` and `cut -d' ' -f4`, computes an output directory from the input file path, then loops over test numbers. Each output file is named `speedtest1-%03d.sql`, and `sed -n` extracts from the matching `-- begin test N` line through the exact `-- end test N` line.

## Control Flow
If the input argument is missing, Bash parameter expansion aborts. If no begin markers are parsed, it prints an error and exits 1. Otherwise it writes each extracted block and prints a tab-separated mapping of test number to generated SQL file.

## State And Persistence Behavior
The script writes output SQL files next to the input file, overwriting existing files with matching names. It does not modify the input. Output content is fully determined by begin/end marker pairs in the speedtest script.

## Dependencies And Integration Points
Dependencies are Bash, `grep`, `cut`, `printf`, and `sed`. It integrates with `speedtest1 --script` output format and any downstream SQL replay or diff tooling that consumes the generated per-test files.

## Risks And Test Signals
Risks include marker-format drift, missing end markers, input paths whose first component is not the desired output directory, and unescaped test numbers in the sed address if the format changes. Test by running it against a known speedtest script, verifying the reported file count matches begin markers, checking a few extracted files include both boundary comments, and confirming generated SQL executes independently where expected.
