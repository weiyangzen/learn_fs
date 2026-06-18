# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmp/mpleft.c

Left-shifts an `mpint`.

Key function:
- `mpleft`: computes `res = b << shift`.

Important behavior:
- Negative left shifts delegate to `mpright`.
- Handles in-place shifts by saving original top.
- Supports whole-limb and partial-limb shifts, zero-fills lower limbs, and normalizes top.
