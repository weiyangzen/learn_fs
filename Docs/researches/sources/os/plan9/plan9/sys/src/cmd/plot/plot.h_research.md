# File Research: sources/os/plan9/plan9/sys/src/cmd/plot/plot.h

Public function prototypes for the Plan 9 plot library.

Key responsibilities:
- Declares drawing primitives, state operations, spline/fill/poly routines, text, color, buffering, and device identity functions.

Notable behavior:
- Uses legacy C prototype style but with typed arguments.
- Function names include Plan 9-specific alternatives such as `plotdisc`, `plotline`, and `plotpoly`.
