# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gp_os2pr.c

OS/2 `%printer%` IODevice implementation.

Key behavior:
- Registers a FileSystem IODevice named `%printer%`.
- Allocates per-device state containing the target queue and scratch filename.
- Validates the requested queue through `pm_find_queue`.
- Opens output as a scratch file with `gp_open_scratch_file`.
- On close, spools the scratch file with `pm_spool` and unlinks it.

Notable dependencies:
- OS/2 spooler support functions from `gp_os2.c`.
- Ghostscript IODevice interfaces from `gxiodev.h`.

Research notes:
- Comments say a pipe/thread implementation was considered but did not work properly for the second Ghostscript thread.
