# File Research: sources/os/plan9/plan9/sys/src/cmd/cmp.c

Implements `cmp` with options `-s` silent, `-l` list all differing bytes, and `-L` include line number for first difference. Accepts optional seek offsets for each file. Reads both files in 64 KiB buffers, compares overlapping spans, tracks byte offset and optionally line count.

Reports seek/open/read errors, first difference, all differences, or EOF mismatch. Silent mode exits with status only.
