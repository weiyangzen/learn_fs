# File Research: sources/os/bsd/netbsd-src/lib/libm/src/e_fmodl.c

Implements long-double kernel `__ieee754_fmodl`.

Key behavior:
- Active under `__HAVE_LONG_DOUBLE`.
- Works directly with `union ieee_ext_u` exponent/significand fields.
- Handles explicit versus implicit integer-bit long-double formats.
- Normalizes subnormal operands by temporary scaling.
- Performs exact fixed-point shift/subtract reduction over high and low significand parts.
- Reconstructs the long-double result and restores dividend sign.

Assumptions are documented: low significand fits in `manl_t`, and high significand fits in signed 64-bit storage with carry room.
