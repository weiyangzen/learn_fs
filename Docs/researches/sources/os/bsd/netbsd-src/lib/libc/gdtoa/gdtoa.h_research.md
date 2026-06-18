# File Research: sources/os/bsd/netbsd-src/lib/libc/gdtoa/gdtoa.h

Purpose: Public interface for the gdtoa conversion library.

Core behavior:
- Defines integer aliases `Long`, `ULong`, and `UShort`.
- Defines `FPI`, which describes binary precision, exponent limits, rounding mode, and sudden-underflow behavior.
- Defines `STRTOG_*` result flags for parsed value class, sign, inexactness, underflow, overflow, and no-memory.
- Provides symbol renaming to NetBSD-private libc names such as `__dtoa`, `__gdtoa`, and `__strtodg_D2A`.
- Declares formatting APIs, parsing APIs, interval APIs, and conversion helpers.

Dependencies:
- Includes generated `arith.h`, `<stddef.h>`, and `<stdint.h>`.
- Provides C++ extern guards and K&R compatibility macros.
