# File Research: sources/os/plan9/9front/sys/src/cmd/venti/srv/cmparenas.c

Command-line byte comparator for two arena partitions with identical arena tables.

Key behavior:
- Reads both arena-part headers/tables and requires exact table equality.
- Iterates listed or all arenas from the table.
- `cmparena` reads arena headers, validates version/length/name, prints decoded header/tail layout, then scans both arena byte ranges block by block and prints hex diffs for mismatching 16-byte chunks.
- `printheader` decodes the arena tail to print data, clump-directory, and tail ranges.
- `-b` controls compare block size, `-s` parses sleep milliseconds but is not used, and `-v` only sets a global not otherwise used meaningfully.

Interactions:
- Uses `unpackarenapart`, `unpackarenahead`, `unpackarena`, and `printarena`.

Notable issues:
- The second header parse after reading `fd1` calls `unpackarenahead(&head, data)` instead of `data1`, so validation of the second arena header appears to incorrectly re-parse the first buffer.
- `fd1` open failure reports `argv[0]` instead of `argv[1]`.
