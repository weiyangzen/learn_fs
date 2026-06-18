# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/int_types.h

This header defines illumos fixed-width, max-width, pointer-width, fast, and least integer typedefs.

Key typedefs:
- Fixed signed: `int8_t`, `int16_t`, `int32_t`, optional `int64_t`.
- Fixed unsigned: `uint8_t`, `uint16_t`, `uint32_t`, optional `uint64_t`.
- `intmax_t`, `uintmax_t` map to 64-bit types when available, otherwise 32-bit.
- `intptr_t`, `uintptr_t` map to long/unsigned long on LP64 and int/unsigned int on ILP32.
- Fast types: `int_fast8_t`, `int_fast16_t`, `int_fast32_t`, optional `int_fast64_t`, and unsigned equivalents.
- Least types: `int_least8_t`, `int_least16_t`, `int_least32_t`, optional `int_least64_t`, and unsigned equivalents.

Data model and ABI notes:
- `int8_t` and 8-bit fast/least signed types use `char` if `_CHAR_IS_SIGNED`, otherwise `signed char`.
- On `_LP64`, `int64_t` is `long`; on ILP32 with long long support, it is `long long`.
- Comment warns that `uint_least16_t` and `uint_least32_t` changes must be mirrored for `char16_t` and `char32_t`.

Dependencies:
- Includes `sys/feature_tests.h`.

Relevance:
- Core type foundation for nearly every kernel and user ABI header in this group.
