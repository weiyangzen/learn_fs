# File Research: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_atanh.c

Implements legacy double `atanh()`. It applies the identity `atanh(x) = 0.5 * log1p(2*x/(1-x))` with sign separated through `copysign()`.

Key behavior:
- Copies the sign into the multiplier `z = +/-0.5`.
- Computes with `|x|` in the quotient.
- On VAX/Tahoe, explicitly handles `|x| == 1` through `infnan(ERANGE)`.
- IEEE invalid/infinite cases are mostly delegated to division and `log1p()`.

Important dependencies: `mathimpl.h`, `copysign()`, and `log1p()`.

Notable risks:
- No explicit IEEE NaN/domain checks for `|x| > 1`; behavior follows arithmetic side effects.
