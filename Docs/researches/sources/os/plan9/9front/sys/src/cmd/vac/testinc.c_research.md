# File Research: sources/os/plan9/9front/sys/src/cmd/vac/testinc.c

Purpose: Small command-line tester for Vac include/exclude pattern files.

Key behavior:
- Requires one include-file argument.
- Loads patterns with `loadexcludefile`.
- Reads newline-delimited paths from standard input and prints `0` or `1` from `includefile` next to each path.

Dependencies:
- Uses the Vac glob/filter helpers and `Biobuf`.

Notable details:
- This is diagnostic tooling for exclusion behavior, not archive processing.
