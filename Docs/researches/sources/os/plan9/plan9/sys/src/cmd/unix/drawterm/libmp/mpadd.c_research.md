# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmp/mpadd.c

Implements multiprecision addition.

Key functions:
- `mpmagadd`: adds absolute values, handling zero and operand size ordering.
- `mpadd`: signed addition; delegates to magnitude subtraction when signs differ.

Important behavior:
- Uses low-level `mpvecadd`.
- Normalizes result and restores sign only when result is nonzero.
