# File Research: sources/os/plan9/plan9/sys/src/cmd/swap.c

This file configures a swap file/device.

Key behavior:
- Takes one path argument.
- If the path is not a kernel device directory, opens it directly for swap.
- If it is a kernel device directory, creates a temporary ORCLOSE file named from `$sysname`.
- Writes the selected path to `/env/swap`.
- Writes the swap file descriptor number to `/dev/swap`.

Important details:
- The command refuses the root path and reports failures through `perror`.
- Temporary swap files are mode `0600`.
- Uses Plan 9’s convention of enabling swap by passing an fd number to `/dev/swap`.

Filesystem relevance:
- Direct: configures virtual memory backing through `/env/swap`, `/dev/swap`, and a file/device path.
