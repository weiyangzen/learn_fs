# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/random.c

Implements Unbound’s random-number abstraction behind `struct ub_randstate`. The file provides `ub_initstate`, `ub_random`, `ub_random_max`, and `ub_randfree`, with backend selection controlled by build configuration.

Key behavior:
- In fuzzing builds, randomness is intentionally deterministic: a counter is incremented and masked to 31 bits, with `ub_random_max` using modulo.
- With `HAVE_SSL` or `HAVE_LIBBSD`, the state is only a placeholder allocation and calls go to `arc4random()` / `arc4random_uniform()`.
- With NSS, `PK11_GenerateRandom` fills a `long int`; failures are fatal because upstream DNS query IDs and source-port choices require secure randomness.
- With Nettle, a Yarrow-256 context is seeded from `getentropy`; unseeded generation logs an error and returns masked zero-derived output.
- `ub_random_max` for NSS/Nettle uses rejection sampling against `MAX_VALUE` to avoid modulo bias.

Important constants and constraints:
- `MAX_VALUE` is `0x7fffffff`, making the public result a portable 31-bit positive range.
- `ub_random_max` assumes `x > 0` and smaller than `2^31`; that precondition is documented in the header, not enforced here.

Integration points:
- Uses `util/log.h` for allocation and entropy errors.
- Uses backend crypto APIs only under compile-time feature macros.
- The `from` seed parameter is ignored in these implementations.
