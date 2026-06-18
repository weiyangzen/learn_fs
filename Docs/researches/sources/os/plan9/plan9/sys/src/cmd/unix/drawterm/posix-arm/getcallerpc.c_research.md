# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/posix-arm/getcallerpc.c

Defines `getcallerpc(void *a)` as `((uintptr*)a)[-1]`.

Role: stack-based caller-PC recovery for ARM drawterm builds.
