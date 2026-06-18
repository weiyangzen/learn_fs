# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/posix-power/getcallerpc.c

Defines `getcallerpc(void *a)` as `((uintptr*)a)[-1]`.

Role: caller-PC recovery for PowerPC drawterm builds.
