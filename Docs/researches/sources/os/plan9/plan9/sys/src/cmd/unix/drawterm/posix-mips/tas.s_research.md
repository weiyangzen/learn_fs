# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/posix-mips/tas.s

MIPS assembly implementation of `tas`.

Behavior:
- Uses `ll`/`sc` loop to atomically store sentinel value `12345` into `*a0`.
- Repeats if store-conditional fails.
- Returns the previous value in `v0`.

Role: MIPS atomic test-and-set primitive for drawterm locking.
