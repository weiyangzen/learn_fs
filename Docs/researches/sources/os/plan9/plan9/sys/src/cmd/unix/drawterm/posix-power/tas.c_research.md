# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/posix-power/tas.c

PowerPC inline assembly implementation of `tas`.

Behavior:
- Uses `sync`, `lwarx`, and `stwcx.` reservation sequence.
- Stores sentinel `0xdeaddead` only when the old value is zero.
- Returns `0` for acquired and `1` for already locked sentinel.
- Reports unexpected values as corrupted.

Notes:
- Contains comments about GCC 2.95.2 and a cache-flush workaround for a 603x issue.
