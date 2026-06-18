# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmp/mpsub.c

Implements multiprecision subtraction.

Key functions:
- `mpmagsub`: subtracts magnitudes, swapping operands and sign if needed.
- `mpsub`: signed subtraction; delegates to magnitude addition when signs differ.

Important behavior:
- Uses low-level `mpvecsub`.
- Normalizes result and adjusts sign only for nonzero differences.
