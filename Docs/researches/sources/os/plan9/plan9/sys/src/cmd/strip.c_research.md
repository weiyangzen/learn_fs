# File Research: sources/os/plan9/plan9/sys/src/cmd/strip.c

This file implements the Plan 9 `strip` utility for executable binaries.

Key behavior:
- Opens a binary, uses libmach `crackhdr` to parse executable headers, and validates magic.
- Computes stripped length as data offset plus data size.
- Reads only text/data content, zeroes symbol and pc/sp table sizes in the exec header, and writes back in place or to `-o ofile`.
- Preserves original file mode.

Important details:
- In-place stripping removes the original before recreating it.
- Already stripped files are reported as such unless an output file was requested.
- Rejects unrecognized binaries and strange computed lengths.

Filesystem relevance:
- Direct file mutation utility for executable files.
