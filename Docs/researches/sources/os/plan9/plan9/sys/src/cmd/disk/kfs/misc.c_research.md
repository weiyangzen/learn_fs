# File Research: sources/os/plan9/plan9/sys/src/cmd/disk/kfs/misc.c

This file contains small numeric, endian, panic, and output helpers.

Key behavior:
- `famd` and `fdf` implement fixed-point filter arithmetic used by throughput/load stats.
- `belong` reads a big-endian 32-bit value from bytes.
- `panic` formats process context, writes to fd 2, calls `abort`, then exits.
- `cprint` writes formatted console-command output to `cmdfd`.
- `print` redirects formatted output to fd 2 because fd 1 may be used for service mode.

Dependencies:
- Uses global `progname`, `procname`, and `cmdfd`.
- Formatting support comes from Plan 9 `vseprint`/`vfprint`.

Role:
- Shared by diagnostics, command output, and fatal paths across KFS.
