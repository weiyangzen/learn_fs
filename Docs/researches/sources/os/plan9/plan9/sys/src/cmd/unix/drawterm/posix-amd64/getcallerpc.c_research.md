# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/posix-amd64/getcallerpc.c

Defines `getcallerpc(void *a)` by returning `((uintptr*)a)[-1]`.

This is the same pointer-width stack-slot approach used by several drawterm architecture ports.
