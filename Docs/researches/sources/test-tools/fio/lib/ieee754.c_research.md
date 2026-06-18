# sources/test-tools/fio/lib/ieee754.c

Purpose: serializes and deserializes floating-point values into IEEE-754-style integer bit patterns.

Important APIs/functions: `pack754(long double f, unsigned bits, unsigned expbits)` and `unpack754(uint64_t i, unsigned bits, unsigned expbits)`. The header wraps these for double-sized 64-bit values.

Control flow: packing handles zero, records sign, normalizes into `[1,2)`, computes significand and biased exponent, and combines sign/exponent/significand bits. Unpacking reverses that process by extracting significand, applying exponent bias, and restoring sign.

State/persistence: pure conversion helpers; no state. Used when fio wants stable binary representation independent of native floating layout.

Dependencies/integration: public-domain algorithm from Beej's guide, included through `ieee754.h`. Used by stats structures that store `fio_fp64_t`.

Risks/test signals: does not explicitly handle NaN, infinities, denormals, or overflow. Tests should round-trip zero, positive/negative normal doubles, large/small finite values, and known bit encodings.
