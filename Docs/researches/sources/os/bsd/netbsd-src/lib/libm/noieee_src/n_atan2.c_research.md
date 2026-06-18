# File Research: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_atan2.c

Implements legacy double `atan2(y, x)` using K.C. Ng’s argument-reduction scheme. It reduces by quadrant and by ratio interval, then evaluates a polynomial for atan on a small interval.

Key behavior:
- Handles NaNs, zero axes, infinities, and signed quadrants explicitly.
- Reduces `t = y/x` into one of several intervals: near `0`, `1/2`, `1`, `3/2`, or infinity.
- Uses split constants for `atan(1/2)`, `atan(3/2)`, `pi/4`, `pi/2`, and `pi`.
- Evaluates an odd polynomial in reduced `t`, with an additional `a12` term on VAX/Tahoe.
- Applies quadrant correction through `PI - z` and `copysign()`.

Important dependencies: `mathimpl.h`, `copysign()`, `finite()`, `logb()`, and `scalb()`.

Notable risks:
- The file intentionally uses machine-rounded `PI`, so results are consistent with the old trig system rather than necessarily modern correctly rounded libm expectations.
