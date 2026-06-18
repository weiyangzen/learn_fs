# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/int_const.h

This header implements ISO C integer constant macros for illumos fixed-width integer types.

Key definitions:
- `__CONCAT__(A,B)` token pasting helper.
- `INT8_C`, `INT16_C`, `INT32_C`, `INT64_C`.
- `UINT8_C`, `UINT16_C`, `UINT32_C`, `UINT64_C`.
- `INTMAX_C`, `UINTMAX_C`.

Data model behavior:
- On `_LP64`, 64-bit constants use `l`/`ul` suffixes.
- On `_ILP32` with `_LONGLONG_TYPE`, 64-bit constants use `ll`/`ull`.
- Without long long support, max constants fall back to unsuffixed values for 32-bit max types.

Dependencies:
- Includes `sys/feature_tests.h`.

Relevance:
- Standards and ABI support for fixed-width constants. Indirectly important across kernel and user headers.
