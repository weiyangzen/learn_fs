# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sema_impl.h

## Role

Defines the private in-kernel semaphore representation used underneath the public `ksema_t` interface.

## Key Interfaces

- `sema_impl_t` contains:
  - `s_slpq`: sleep queue pointer to blocked threads.
  - `s_count`: current semaphore count.

## Dependencies

Includes basic types and machine lock definitions outside assembly builds.

## Risk Notes

The public `ksema_t` in `semaphore.h` is opaque but sized to fit this representation. Layout changes must preserve that relationship and any assembly/kernel synchronization assumptions.
