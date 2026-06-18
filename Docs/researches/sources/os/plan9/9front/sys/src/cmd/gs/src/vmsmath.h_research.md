# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/vmsmath.h

Substitute `math.h` for GNU C on VAX/VMS.

Key points:
- Defines `HUGE_VAL` based on `CC$gfloat`.
- Declares classic double-returning math functions manually: trigonometric, hyperbolic, exponential/log, power, modulus, square root, rounding, absolute, complex absolute, and hypotenuse.
- Wrapped in `vmsmath_INCLUDED` and `__MATH` guards.

Dependencies and interactions:
- Used by VMS builds when the normal system math header is unavailable or unsuitable.
- Related to the broader Ghostscript portability headers such as `math_.h`.

Research relevance:
- Historical VAX/VMS compiler compatibility shim for math declarations.
