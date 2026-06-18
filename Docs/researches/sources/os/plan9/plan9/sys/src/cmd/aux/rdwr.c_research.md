# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/rdwr.c

Tiny interactive read/write utility for Plan 9 device files or other seekable files.

Core behavior:
- Opens one file `ORDWR`.
- Optional `-w` performs an initial read and prints the result.
- Repeatedly prompts with `> `, reads a line from stdin, writes it to offset zero without the trailing newline, seeks back to zero, then reads and prints the file contents.

Dependencies and integration:
- Standalone libc command.
- Useful for manually poking text control files in `/dev`, `/proc`, or device namespaces.

Notable risks:
- Assumes the input line has a trailing newline and writes `n-1` bytes.
- Uses fixed 8192-byte read buffer and 1000-byte stdin reads.
