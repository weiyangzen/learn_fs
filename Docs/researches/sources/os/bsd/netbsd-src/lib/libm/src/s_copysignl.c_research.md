# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_copysignl.c

Implements `copysignl()` for real long double and IBM double-double long double. Extended formats copy the sign field directly; IBM long double applies `copysign()` to both component doubles.

Key behavior: compiled only when `__HAVE_LONG_DOUBLE` or `__HAVE_IBM_LONGDOUBLE` is set.

Important dependencies: `namespace.h`, `<machine/ieee.h>`, `union ieee_ext_u`, `union ldbl_u`, and `copysign()`.

Notable risks: IBM double-double handling assumes both component signs should be synchronized.
