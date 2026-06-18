# File Research: sources/os/plan9/plan9/sys/src/cmd/read.c

Read status: complete, 91 lines.

This is a small `read` command. It reads one line by default, or multiple lines with `-m` or `-n nlines`, from stdin or named files, writing the data to stdout.

`line` grows a buffer in 1024-byte chunks, reads byte-by-byte until newline or EOF, writes any accumulated line, and records `"eof"` status when no bytes are read. `lines` repeats `line` according to option state. `main` handles options and file opening.

Filesystem relevance: simple file input utility using `open`, `read`, `write`, and `close`.
