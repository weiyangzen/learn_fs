# sources/security-integrity/selinux/libsepol/src/private.h

## Purpose
`private.h` centralizes libsepol internal portability helpers for endian conversion, array sizing, overflow-safe input accounting, compatibility lookup, policy-file I/O declarations, and a `reallocarray()` fallback.

## Important APIs and Integration
Endian macros normalize policy binary fields to little-endian. `ARRAY_SIZE`, `min`, `max`, `spaceship_cmp`, `is_saturated`, and `zero_or_saturated` are common helpers. `exceeds_available_bytes()` detects count-size multiplication overflow and memory-backed input overrun. `ignore_unsigned_overflow_` suppresses intentional hash overflow under Clang UBSAN. `services.c` implements `next_entry()`, `put_entry()`, and `str_read()` declared here; read/write code consumes them.

## Risks and Test Signals
`min` and `max` evaluate arguments more than once. `exceeds_available_bytes()` protects only `PF_USE_MEMORY`; stdio relies on read failure. Cross-endian builds, short memory input tests, oversized counts, and UBSAN builds provide useful signals.
