# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/win32-386/getcallerpc.c

Defines `getcallerpc(void *a)` as `((uintptr*)a)[-1]`.

Role: caller-PC recovery for Win32 i386 drawterm builds.
