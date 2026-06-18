# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/getpid.c

This file provides a Plan 9-style process id helper.

Key behavior:
- `getpid` returns a pid derived from the current hosted `Proc`.

Important details:
- Uses drawterm's process model, not necessarily the host OS pid.
