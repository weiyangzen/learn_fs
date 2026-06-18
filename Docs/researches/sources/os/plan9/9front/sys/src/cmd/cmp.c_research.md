# File Research: sources/os/plan9/9front/sys/src/cmd/cmp.c

Implements Plan 9 `cmp` for bytewise file comparison with optional offsets.

Flags: `-s` silent status-only, `-l` list all differing bytes with hex values, and `-L` include line number in first-difference output/counting. Usage accepts `file1 file2 [offset1 [offset2]]`.

`seekoff` validates numeric offset arguments and seeks each file. The main loop reads both files into 64 KiB buffers, compares common spans with `memcmp`, then scans byte-by-byte on mismatch to report differences and track newline counts.

Exit status distinguishes identical, differ, EOF difference, read/open/seek errors through Plan 9 `exits` strings.

Implementation note: it reports EOF on the shorter file after the number of equal bytes processed.
