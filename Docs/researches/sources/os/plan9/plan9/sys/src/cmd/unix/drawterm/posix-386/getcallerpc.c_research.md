# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/posix-386/getcallerpc.c

Defines `getcallerpc(void *a)` for i386-style stack frames by returning `((uintptr*)a)[-1]`.

Purpose: expose the saved caller program counter expected by Plan 9 libc/debugging code.

Assumption: caller passes an address positioned so the previous pointer-width slot contains the return address.
