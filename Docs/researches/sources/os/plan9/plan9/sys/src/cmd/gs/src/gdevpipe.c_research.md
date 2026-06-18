# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpipe.c

## Role

`gdevpipe.c` implements Ghostscript’s `%pipe%` IODevice using `popen()` and `pclose()`.

## API

- Exposes `gs_iodev_pipe` with device name `%pipe%` and category `Special`.
- `pipe_fopen()` rejects access modes containing `+`, opens a process pipe with `popen()`, maps `errno` to Ghostscript errors, and copies the resolved name when requested.
- `pipe_fclose()` closes the pipe with `pclose()`.

## Dependencies

Uses Ghostscript IODevice interfaces, `pipe_.h`, `stdio_.h`, `errno_.h`, string helpers, and Ghostscript error mapping.

## Risks And Invariants

- Pipes are explicitly treated as non-positionable by rejecting read/write update modes.
- The command string is passed directly to `popen()`, so security depends on Ghostscript’s broader `%pipe%` access policy and sandbox settings outside this file.
- `pipe_fclose()` ignores the process exit status from `pclose()`.
