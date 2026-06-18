# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libdraw/icossin.c

Provides integer sine/cosine lookup for degree angles.

Key data/function:
- `sinus[91]`: quarter-wave sine table scaled to `1024`.
- `icossin`: normalizes degrees to `0..359`, maps to the correct quadrant, and returns scaled cosine and sine.

Used by arc and geometry code where deterministic integer math is preferred over floating point.
