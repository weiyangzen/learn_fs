# File Research: sources/os/bsd/netbsd-src/lib/libutil/compat/compat_parsedate.c

## Purpose
Compatibility wrapper for old `parsedate()` returning 32-bit time.

## Key Details
- Accepts `const int32_t *` as the optional base time.
- Converts it to `time_t` when present.
- Calls `__parsedate50`.
- Casts the result back to `int32_t`.

## Dependencies and Role
- Bridges old time ABI to the current `parsedate.y` implementation.
- Potential truncation is inherent to the compatibility ABI.
