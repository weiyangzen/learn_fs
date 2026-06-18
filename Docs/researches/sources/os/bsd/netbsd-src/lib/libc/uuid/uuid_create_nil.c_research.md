# File Research: sources/os/bsd/netbsd-src/lib/libc/uuid/uuid_create_nil.c

## Purpose
Implements `uuid_create_nil()`, producing the all-zero UUID.

## Behavior
Zeroes the caller-provided `uuid_t` with `memset()` and reports `uuid_s_ok` when `status` is non-null.

## Dependencies
Depends on `string.h`, `uuid.h`, libc namespace support, and weak aliasing to `_uuid_create_nil`.

## Risks And Notes
No null check is performed for the output UUID pointer; callers must pass valid storage.
