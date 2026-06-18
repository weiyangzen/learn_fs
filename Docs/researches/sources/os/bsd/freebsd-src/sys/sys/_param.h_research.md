# File Research: sources/os/bsd/freebsd-src/sys/sys/_param.h

Small parameter and rounding macro subset.

Key elements:
- Defines `NBBY`, `NBPW`, `nitems`, `howmany`, `rounddown`, `roundup`, `rounddown2`, `roundup2`, and `powerof2`.
- Power-of-two alignment delegates to `__align_down` and `__align_up`.

Dependencies:
- Assumes alignment helpers are available from surrounding headers.

Research notes:
- These macros are foundational in kernel and filesystem sizing, block rounding, array counts, and page calculations.
