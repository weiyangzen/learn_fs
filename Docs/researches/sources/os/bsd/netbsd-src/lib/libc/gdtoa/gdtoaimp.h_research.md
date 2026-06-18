# File Research: sources/os/bsd/netbsd-src/lib/libc/gdtoa/gdtoaimp.h

Purpose: Internal implementation header for the gdtoa library.

Core behavior:
- Describes supported architecture modes: IEEE big/little endian, VAX, and IBM floating point.
- Enables NetBSD defaults: `INFNAN_CHECK`, `USE_LOCALE`, and thread support under `_REENTRANT`.
- Defines double word access macros, exponent/significand masks, constants, `Bigint`, packing mode, lock macros, and symbol renames.
- Declares all internal helpers and shared power-of-ten tables.
- Defines NaN word selection based on endian and generated `gd_qnan.h`.

Dependencies:
- Includes `gdtoa.h`, `gd_qnan.h`, libc headers, optional `fenv.h`, and `reentrant.h`.
- Requires exactly one architecture floating-point format macro from generated `arith.h`.
