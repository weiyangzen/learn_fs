# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/semaphore.h

## Role

Provides the public illumos kernel semaphore interface documented by `semaphore(9F)`.

## Key Interfaces

- `ksema_type_t` distinguishes `SEMA_DEFAULT` and `SEMA_DRIVER`.
- `ksema_t` is an opaque two-word semaphore object.
- Kernel macro `SEMA_HELD(x)` maps to `sema_held(x)`.
- Kernel functions:
  - `sema_init()`
  - `sema_destroy()`
  - `sema_p()`
  - `sema_p_sig()`
  - `sema_v()`
  - `sema_tryp()`
  - `sema_held()`

## Risk Notes

This is a stable driver-facing synchronization ABI. The opaque object size and initialization contract must remain compatible with compiled drivers.
