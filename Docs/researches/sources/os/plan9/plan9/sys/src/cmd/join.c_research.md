# File Research: sources/os/plan9/plan9/sys/src/cmd/join.c

## Purpose
Plan 9 implementation of the Unix `join` command for joining two sorted files on selected fields.

## Main Behavior
Parses `-1`, `-2`, `-j`, `-a`, `-e`, `-t`, and `-o`. It opens two files or stdin, requires at least one randomly seekable input, and uses `Bseek` to revisit duplicate-key ranges.

## Data Model
Input lines are read through Bio into fixed `Rune` buffers, split into up to `NFLD` fields, and compared with `runestrcmp`. Default separators are space and tab; with `-t`, a single explicit separator is used.

## Output
Default output prints the join field followed by non-join fields from file 1 and file 2. `-o` controls explicit field output, including field `0` for the join key. Missing fields can use the `-e` replacement.

## Risks and Limits
Lines are bounded by `Bsize`; truncated lines set `discard` and cause a final fatal error. The algorithm assumes sorted inputs and seekability for duplicate group replay.
