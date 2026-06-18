# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gp_mktmp.c

Read status: complete.

Purpose: replacement `mktemp` implementation for platforms that lack one.

Main logic:
- Requires the input filename to end in `XXXXXX`.
- Replaces that suffix with `AA.AAA`.
- Calls `stat` repeatedly and increments characters from the end, skipping dots and rolling `Z` back to `A`, until it finds a non-existing name.
- Returns `NULL` for invalid input or exhausted name space.

Filesystem/storage relevance:
- Generates temporary file names for platform scratch-file code.

Notable behavior:
- Name generation is race-prone because existence checking and later opening are separate.
- The suffix pattern is DOS-like (`AA.AAA`) rather than preserving six contiguous characters.
