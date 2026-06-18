# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/posix-amd64/tas.c

Implements `tas(long *x)` with amd64 inline assembly using `xchgl` through `%rcx`.

Behavior mirrors the i386 implementation:
- Atomically writes `1`.
- Returns previous `0` or `1`.
- Treats other values as corrupted lock state and returns locked.

Role: drawterm spin-lock primitive for POSIX amd64.
