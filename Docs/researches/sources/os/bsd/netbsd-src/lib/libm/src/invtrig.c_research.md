# File Research: sources/os/bsd/netbsd-src/lib/libm/src/invtrig.c

This file is a long-double inverse-trigonometry coefficient dispatch source.

If long double is available, it includes either `../ld80/invtrig.c` or `../ld128/invtrig.c` depending on `LDBL_MANT_DIG`; unsupported long-double formats are rejected. It contains no public functions or coefficients directly in this wrapper.

Dependencies are `math.h`, `<machine/float.h>`, and the selected ld80/ld128 implementation.
