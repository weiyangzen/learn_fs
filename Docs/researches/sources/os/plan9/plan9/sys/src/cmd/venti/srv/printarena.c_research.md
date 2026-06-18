# File Research: sources/os/plan9/plan9/sys/src/cmd/venti/srv/printarena.c

Purpose: Command-line utility to inspect a single arena file.

Key behavior:
- Opens an arena file read-only/direct, reads and prints the arena head, initializes an arena object, and walks clumps from a specified or zero offset.
- For each clump, checks magic, loads data, verifies score/type unless marked corrupt, and prints offset, score, type, and uncompressed size.
- Prints the final end offset.

Dependencies:
- Uses arena metadata parsing, clump loading, score validation, partition I/O, and disk cache setup.

Notable details:
- Supports `-o` to choose the arena file offset.
