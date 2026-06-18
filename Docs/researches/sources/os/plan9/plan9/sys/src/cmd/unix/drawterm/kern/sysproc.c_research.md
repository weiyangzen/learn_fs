# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/sysproc.c

This file provides the minimal process-exit syscall for drawterm.

Key behavior:
- `sysexits` optionally prints an exit status string and terminates the host process with `exit(0)`.

Important details:
- It ignores Plan 9 wait status propagation; drawterm runs as a hosted application.
