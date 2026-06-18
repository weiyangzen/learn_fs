# File Research: sources/os/bsd/netbsd-src/lib/libc/uuid/uuid_compare.c

## Purpose
Implements `uuid_compare()`, a DCE-style ordering comparison for two `uuid_t` values.

## Behavior
Sets `status` to `uuid_s_ok` when provided. Treats equal pointers as equal, treats `NULL` as a nil UUID, and orders nil UUIDs before non-nil UUIDs. Non-null UUIDs are compared field-by-field in UUID logical order: `time_low`, `time_mid`, `time_hi_and_version`, clock sequence bytes, then node bytes.

## Dependencies
Depends on `uuid_is_nil()`, `memcmp()`, `uuid.h`, and libc namespace support.

## Risks And Notes
The comparison is structural rather than raw-memory order, avoiding host padding issues. `time_low` subtraction is widened to `int64_t` before reduction to `-1/0/1`.
