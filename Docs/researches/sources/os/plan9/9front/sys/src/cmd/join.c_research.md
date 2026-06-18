# File Research: sources/os/plan9/9front/sys/src/cmd/join.c

This is the Plan 9 implementation of the `join` text utility.

Key behavior:
- Joins two sorted input files on selected fields.
- Supports `-1`, `-2`, `-j`, `-a`, `-e`, `-t`, and `-o` output field selection.
- Handles UTF input by converting lines to `Rune` buffers before field splitting/comparison.
- Requires at least one randomly seekable input and has separate algorithms depending on which file can seek.
- Outputs default joined fields or explicit field lists, with null replacement for missing fields.

Research notes:
- Maximum fields per line is fixed at `NFLD=100`; long/truncated lines set `discard`.
- Uses stdio rather than Plan 9 `Biobuf`.
