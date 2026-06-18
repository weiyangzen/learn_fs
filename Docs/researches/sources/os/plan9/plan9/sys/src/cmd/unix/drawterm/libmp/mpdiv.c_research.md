# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmp/mpdiv.c

Implements multiprecision division using Knuth Algorithm D.

Key function:
- `mpdiv`: computes optional quotient and remainder.

Important behavior:
- Aborts on division by zero.
- Handles dividend smaller than divisor as a quick case.
- Normalizes divisor/dividend by left-shifting until divisor high bit is set.
- Estimates quotient digits with `mpdigdiv`, corrects overestimates, subtracts `v*qd`, and adds back if necessary.
- Restores quotient sign and remainder sign.
