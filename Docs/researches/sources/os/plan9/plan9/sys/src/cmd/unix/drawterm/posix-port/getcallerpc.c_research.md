# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/posix-port/getcallerpc.c

Portable fallback `getcallerpc(void *a)` implementation.

Behavior:
- Ignores `a`.
- Returns `0`.

Role: safe fallback when caller-PC recovery is unavailable or unsupported.
