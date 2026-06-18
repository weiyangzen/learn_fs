# File Research: sources/os/bsd/netbsd-src/lib/libc/uuid/uuid_is_nil.c

## Purpose
Implements `uuid_is_nil()`, testing whether a UUID is the nil UUID.

## Behavior
Sets status to `uuid_s_ok`. Treats a `NULL` pointer as nil. Otherwise compares the UUID against a static zero-initialized `uuid_t`.

## Dependencies
Depends on `memcmp()`, `uuid.h`, and weak aliasing to `_uuid_is_nil`.

## Risks And Notes
The static initializer zeros the whole object through C initialization rules. As with `uuid_equal()`, this relies on valid `uuid_t` object representation being safe for byte comparison.
