# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/refstr.c

## Purpose

Small reference-counted string utility for kernel users that need immutable strings with shared ownership.

## Key Interfaces

- `refstr_alloc()` allocates one object containing size, 32-bit reference count, and NUL-terminated string data.
- `refstr_value()` returns the stored string pointer or `NULL`.
- `refstr_hold()` atomically increments the reference count.
- `refstr_rele()` atomically decrements and frees the exact allocation size when the count reaches zero.

## Dependencies

Uses `kmem_alloc()`, `kmem_free()`, `strlen()`, `strcpy()`, and `atomic_inc_32()`/`atomic_dec_32_nv()`.

## Notes for Future Work

- `refstr_alloc()` asserts the computed allocation size fits in `uint32_t`.
- The API assumes callers do not mutate the returned string and do not release more times than held.
