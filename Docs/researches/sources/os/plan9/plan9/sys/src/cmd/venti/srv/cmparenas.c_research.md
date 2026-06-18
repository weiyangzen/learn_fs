# File Research: sources/os/plan9/plan9/sys/src/cmd/venti/srv/cmparenas.c

Compares two arena partition files byte-for-byte at the arena level. It reads both arena partition headers and tables, requires identical tables, then compares selected arena names or all arenas.

`readap()` unpacks the arena partition header and reads the arena table. `cmparena()` validates arena headers and tail metadata, prints structural ranges using `printheader()`, then reads both arena byte streams block by block and reports hex diffs for mismatching 16-byte spans.

The command supports custom compare block size (`-b`), optional sleep between reads (`-s`), and verbosity. It is useful for replica comparison or confirming copied arena partitions remain identical.
