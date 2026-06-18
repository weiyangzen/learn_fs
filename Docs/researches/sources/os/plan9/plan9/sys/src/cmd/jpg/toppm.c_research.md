# File Research: sources/os/plan9/plan9/sys/src/cmd/jpg/toppm.c

## Purpose
Converts a Plan 9 image to ASCII Netpbm PPM/PGM/PBM output.

## Behavior
Reads stdin or one file as `Memimage`, converts unsupported channel layouts to GREY/RGB through `memmultichan`, then writes with `memwriteppm`.

## Options
`-c` supplies a comment; comments containing newlines are rejected. Without a comment for file input, it emits a “Converted by Plan 9 from …” comment.
