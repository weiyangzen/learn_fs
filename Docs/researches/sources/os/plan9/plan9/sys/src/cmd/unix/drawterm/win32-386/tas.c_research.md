# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/win32-386/tas.c

Implements Win32 i386 `tas(long *x)` with the same `xchgl` inline assembly pattern as `posix-386/tas.c`.

Behavior:
- Atomically stores `1`.
- Returns prior `0` or `1`.
- Logs corrupted values and returns locked for unexpected state.
