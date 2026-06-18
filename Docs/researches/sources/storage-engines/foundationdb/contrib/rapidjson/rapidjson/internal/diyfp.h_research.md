# sources/storage-engines/foundationdb/contrib/rapidjson/rapidjson/internal/diyfp.h

Purpose: This header implements `internal::DiyFp`, the normalized 64-bit significand/exponent representation used by Grisu2 double-to-string and string-to-double conversion.

Important APIs and types: `DiyFp` exposes constructors from raw `(uint64_t, int)` and `double`, subtraction, multiplication, `Normalize()`, `NormalizeBoundary()`, `NormalizedBoundaries()`, `ToDouble()`, IEEE-754 constants, and public fields `f` and `e`. Free helpers `GetCachedPowerByIndex`, `GetCachedPower`, and `GetCachedPower10` return cached powers of ten as `DiyFp` plus decimal exponent metadata.

Control flow: The double constructor decodes exponent and significand bits, adding the hidden bit for normal values. Multiplication produces the high half of a 128-bit product with rounding. Normalization shifts the significand until the top bit is set. Boundary computation derives minus/plus rounding bounds for shortest decimal generation. Cached power selection uses a precomputed table from `10^-348` through `10^340`.

State and persistence behavior: There is no mutable global state. Static lookup tables hold cached powers. All conversion state is local value data.

Dependencies and integration points: It depends on `rapidjson.h` and optional compiler intrinsics. `dtoa.h` uses it for Grisu2; `strtod.h` uses cached powers and `ToDouble()` in approximation.

Risks: Bit-level IEEE-754 assumptions are central. Multiplication and normalization have compiler-specific branches. Cached-power table indexes must stay aligned with exponent arrays. NaN/Inf handling is not performed here and must be filtered by callers.

Test signals: Verify decoded components for normal, denormal, and boundary doubles; multiplication rounding; normalized boundaries for powers of two; cached power exponent/index selection; and round-trip support through dtoa/strtod tests.
