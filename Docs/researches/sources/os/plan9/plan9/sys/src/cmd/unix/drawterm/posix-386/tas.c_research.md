# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/posix-386/tas.c

Implements `tas(long *x)` with i386 inline assembly using `xchgl` to atomically exchange `1` into `*x`.

Behavior:
- Returns the previous value when it is `0` or `1`.
- Prints `canlock: corrupted` and returns locked (`1`) for unexpected values.

Role: machine-dependent primitive for Plan 9 spin locks on POSIX i386.
