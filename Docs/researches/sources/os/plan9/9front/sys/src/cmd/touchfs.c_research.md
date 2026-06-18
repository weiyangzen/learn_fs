# File Research: sources/os/plan9/9front/sys/src/cmd/touchfs.c

Read completely: 66 lines, 1120 bytes.

Filter for Plan 9 `mkfs` archive streams. It reads archive header lines from stdin, rewrites the fifth field to a supplied timestamp, copies each file payload unchanged, and stops at `end of archive`.

Key behavior:
- Expects exactly one argument: seconds timestamp.
- Uses `tokenize` on each archive header and requires six fields.
- `Bpass` copies the following payload byte count exactly, diagnosing corrupt or premature archives.

Dependencies:
- Uses `Biobuf`, `quotefmtinstall`, `Brdline`, `Bprint`, `Bread`, and `Bwrite`.

Reliability notes:
- The archive parser assumes header lines have no embedded newline surprises after quote tokenization.
- Payload size is trusted after `strtoul`; malformed sizes can desynchronize the stream.
