# File Research: sources/os/bsd/netbsd-src/lib/libm/noieee_src/n_asincos.c

Implements legacy `asin()`, `asinf()`, `acos()`, and `acosf()`. The double functions reduce inverse trig to `atan2()` and `sqrt()` identities; float functions call the double versions and cast.

Key behavior:
- `asin(x)` computes `atan2(x, sqrt(1-x*x))` for `|x| <= 0.5`, and uses `2*(1-|x|) - (1-|x|)^2` near `|x| = 1` for better accuracy.
- `acos(x)` computes `2*atan2(sqrt((1-x)/(1+x)), 1)`, with a special `x == -1` path.
- NaNs are returned unchanged on IEEE targets.
- Weak aliases map public names to internal names.

Important dependencies: `namespace.h`, `mathimpl.h`, `atan2()`, `sqrt()`, and `copysign()`.

Notable risks:
- Modern domain handling is implicit; `|x| > 1` reaches invalid `sqrt()`/division behavior.
