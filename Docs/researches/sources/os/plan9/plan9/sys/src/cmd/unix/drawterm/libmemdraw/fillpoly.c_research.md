# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmemdraw/fillpoly.c

Fills polygons using scan conversion.

Key functions:
- `memfillpoly`: public wrapper.
- `_memfillpolysc`: builds segment tables and runs scan conversion.
- `xscan`: primary horizontal scan-line filling with winding count.
- `yscan`: optional detail pass for thin/edge cases.
- `zsort`, `ycompare`, `xcompare`, `zcompare`: active-edge ordering helpers.
- `sdiv`, `mod`, `smuldivmod`: signed arithmetic helpers for fixed-point edge stepping.

Important behavior:
- Vertices are shifted to fixed-point form when needed.
- Uses winding mask `w` to decide filled intervals.
- Filling delegates to `memdraw` spans or points with `memopaque`.
