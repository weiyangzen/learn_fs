# File Research: sources/os/plan9/9front/sys/src/cmd/comm.c

Implements `comm`, comparing two sorted text files and printing three columns: lines only in file1, only in file2, and common lines.

Flags `-1`, `-2`, and `-3` suppress the corresponding output columns while adjusting tab leaders.

Uses `Biobuf` input and fixed 2048-byte line buffers. `rd` reads one line, terminates at newline or near buffer capacity, and strips the newline by replacing it with NUL. `compare` performs lexical byte comparison.

The main loop reads one current line from each file, compares, writes the appropriate column through `wr`, and advances the relevant file. `copy` drains the remaining file when the other reaches EOF.

Supports `-` as stdin through `/fd/0`.
