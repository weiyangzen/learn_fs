# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmp/mpright.c

Right-shifts an `mpint`.

Key function:
- `mpright`: computes `res = b >> shift`.

Important behavior:
- Negative right shifts delegate to `mpleft`.
- Supports whole-limb and partial-limb shifts.
- Handles in-place operation and trims leading zero limbs.
