# File Research: sources/os/bsd/netbsd-src/lib/libm/ld128/b_tgammal.c

This ld128 file is not a full `tgammal` implementation. It creates an imprecise long-double wrapper around the double-precision `tgamma()`.

The macro `DECLARE_IMPRECISE(tgamma)` defines `imprecise_tgammal(long double v)` and returns `tgamma(v)`, losing precision whenever `long double` has more than 53 mantissa bits. If `LDBL_MANT_DIG > 53`, `WARN_IMPRECISE` emits a linker warning through `__warn_references`.

The public symbol is weak-aliased so a more accurate implementation from another library can override it. This makes the file a compatibility fallback rather than a numerical implementation.

Dependencies are `<float.h>`, `<math.h>`, `__weak_alias`, and `__warn_references`.
