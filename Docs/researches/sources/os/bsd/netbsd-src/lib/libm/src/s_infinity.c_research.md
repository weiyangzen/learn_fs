# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_infinity.c

Defines the legacy `__infinity` byte array for double positive infinity.

Key behavior: chooses byte order at compile time using `BYTE_ORDER`.

Important dependencies: `<sys/types.h>` endian definitions.

Notable risks: only encodes IEEE double infinity bytes.
