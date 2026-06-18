# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gp_stdin.c

Portable buffered stdin reader for platforms without unbuffered reads.

Key behavior:
- Implements `gp_stdin_read` with `fread`.
- Reads one byte when `interactive` is true, otherwise reads up to the requested length.

Research notes:
- Comments note this is portable but slow for interactive stdin because it reads one byte at a time.
