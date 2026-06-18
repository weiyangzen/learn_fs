# File Research: sources/os/bsd/netbsd-src/sys/sys/cdbr.h

## Scope

Declares the constant database reader API.

## APIs And Behavior

- Defines `CDBR_DEFAULT`.
- Opaque `struct cdbr`.
- Userland-only `cdbr_open(path, flags)` plus shared `cdbr_open_mem`.
- Declares `cdbr_entries`, `cdbr_get`, `cdbr_find`, and `cdbr_close`.
- `cdbr_open_mem` accepts a memory buffer, size, close callback, and callback cookie.

## Dependencies

- Includes `sys/cdefs.h`.
- Kernel/standalone include `sys/types.h`; userland includes `inttypes.h` and `stddef.h`.

## Risks And Invariants

- API returns data by pointer and size, so lifetime is tied to the open database object.
- Userland file-open API is intentionally absent in kernel/standalone builds.
