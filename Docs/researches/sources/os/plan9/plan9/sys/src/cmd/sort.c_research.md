# File Research: sources/os/plan9/plan9/sys/src/cmd/sort.c

Plan 9 sort implementation with external merge support.

Key behavior:
- Parses classic and POSIX-style sort options, including fields, `-k`, `-t`, `-o`, `-T`, `-c`, `-u`, `-bdfgiMnrw`, and debug `-v`.
- Reads input lines from files or stdin, ensuring final newline if needed.
- Builds binary sort keys per line based on global and field-specific options.
- Sorts in memory with radix sort for larger sets and insertion/bubble cleanup for small partitions.
- Spills sorted runs to temporary files when line count exceeds `-l`/default limit, then merges runs.
- Supports order checking with `-c` and unique output with `-u`.

Important details:
- Temporary files are named `sort.<pid>.<n>` under `/tmp` or `-T`.
- At most 10 temporary runs are merged at once; additional merge passes create more temp files.
- Numeric key generation normalizes sign, decimal point position, exponent, and reverse order into byte-sortable keys.
- Month sorting maps three-letter month names.
- `kcmp()` compares only the common key length, reflecting key encodings with terminators.

Filesystem relevance:
- Direct: reads input files, writes optional output file, and uses temporary files for external sorting.
