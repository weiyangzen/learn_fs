# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpipe.c

Ghostscript `%pipe%` IODevice implementation.

Key behavior:
- Defines `gs_iodev_pipe` with device name `%pipe%` and type `Special`.
- Most filesystem-like operations are disabled: delete, rename, status, enumeration, params, and direct device open.
- `pipe_fopen` rejects access modes containing `+` because pipes are not positionable even if some platforms accept such modes.
- Opens the named command with `popen`, mapping `errno` to Ghostscript file errors on failure.
- Copies the resolved name into `rfname` when provided.
- `pipe_fclose` closes the pipe with `pclose`.

Research notes:
- This is an IODevice bridge to OS pipes; it is the only file here with direct process/pipe behavior.
- It does not implement general filesystem semantics.
