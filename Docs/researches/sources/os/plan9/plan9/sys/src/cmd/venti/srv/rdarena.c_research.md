# File Research: sources/os/plan9/plan9/sys/src/cmd/venti/srv/rdarena.c

Purpose: Extracts a named arena from an arena partition to standard output.

Key behavior:
- Opens an arena partition read-only/direct, locates the named arena, and writes the arena header, body, and trailer to stdout.
- Uses a buffer at least as large as the arena block size and otherwise `MaxIoSize`.
- Optional `-q` suppresses progress output; `-v` prints arena partition metadata.

Dependencies:
- Uses arena partition loading, disk cache, partition reads, and raw stdout writes.

Notable details:
- Output is binary arena data suitable for backup or transfer.
