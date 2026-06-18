# File Research: sources/os/bsd/netbsd-src/lib/libc/uuid/uuid_to_string.c

## Purpose
Implements `uuid_to_string()`, allocating a canonical dashed lowercase hex UUID string.

## Behavior
Sets status to `uuid_s_ok`. If the output string pointer itself is null, it returns without work. A null UUID input is formatted as nil. Uses `asprintf()` to allocate the result and reports `uuid_s_no_memory` if allocation fails.

## Dependencies
Depends on `asprintf()`, `uuid.h`, and standard formatting.

## Risks And Notes
The caller owns the allocated string. The API does not clear `*s` before `asprintf()`, so callers should not assume it changes on every failure mode except the direct allocation result.
