# File Research: sources/os/bsd/netbsd-src/lib/libc/gdtoa/gethex.c

Purpose: Parses hexadecimal floating constants for `strtod` and `strtodg`.

Core behavior:
- Parses `0x`/`0X` significands, optional locale decimal point, and binary `p`/`P` exponent.
- Builds a `Bigint` from hexadecimal digits in little-endian word order.
- Scales to `fpi->nbits`, computes lost bits, and applies rounding mode.
- Handles huge exponents by returning infinity or max finite depending on rounding direction.
- Handles tiny exponents by returning zero or the smallest denormal according to rounding and sign.
- Returns `STRTOG_*` flags and writes the parsed significand/exponent through `bp` and `expt`.

Dependencies:
- Includes `gdtoaimp.h` and optionally `locale.h`.
- Uses `hexdig`, `hexdig_init_D2A`, `Balloc`, `Bfree`, `rshift`, `lshift`, `any_on`, `increment`, and `errno`.
