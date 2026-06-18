# File Research: sources/os/bsd/netbsd-src/lib/libc/uuid/uuid_equal.c

## Purpose
Implements `uuid_equal()`, returning whether two UUIDs represent the same UUID.

## Behavior
Sets status to `uuid_s_ok`. Equal pointers are equal. A `NULL` UUID pointer is treated as nil, so `NULL` equals a nil UUID and not a non-nil UUID. Non-null UUIDs are compared byte-for-byte over `sizeof(uuid_t)`.

## Dependencies
Depends on `uuid_is_nil()`, `memcmp()`, and `uuid.h`.

## Risks And Notes
Byte comparison assumes `uuid_t` has deterministic representation for all fields, including no meaningful uninitialized padding in valid values.
