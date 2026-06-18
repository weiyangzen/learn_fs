# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/serializer.h

## Role

Declares an unstable kernel-only STREAMS serializer interface.

## Key Interfaces

- Opaque `serializer_t`.
- Callback type `srproc_t(mblk_t *, void *)`.
- Kernel functions:
  - `serializer_init()`
  - `serializer_create()`
  - `serializer_enter()`
  - `serializer_wait()`
  - `serializer_destroy()`

## Dependencies

Kernel builds include STREAMS message block definitions and kernel memory allocation support.

## Risk Notes

The header explicitly says it is not public and is unstable. Callers depend on serialized callback execution and must honor message ownership/lifetime conventions.
