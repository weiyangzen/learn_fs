# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/vmsmath.h

Substitute `math.h` for GNU C on VAX/VMS.

Key points:
- Defines `HUGE_VAL` differently based on `CC$gfloat`.
- Declares classic K&R-style prototypes for common math functions: trig, hyperbolic, exp/log, pow, `modf`, `fmod`, `sqrt`, `ceil`, `floor`, `fabs`, `cabs`, and `hypot`.
- Guarded by `vmsmath_INCLUDED` and `__MATH`.

Dependencies and interactions:
- Used where VAX/VMS GNU C lacks a usable system `math.h`.

Research relevance:
- Minimal historical portability wrapper for old VMS compiler environments.
