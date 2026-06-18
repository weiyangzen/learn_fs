# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/posix-mips/getcallerpc.c

Defines `getcallerpc(void *a)` returning `((ulong*)a)[-1]`.

Difference from most other ports: returns `ulong` rather than `uintptr`, matching local MIPS type conventions in this tree.
