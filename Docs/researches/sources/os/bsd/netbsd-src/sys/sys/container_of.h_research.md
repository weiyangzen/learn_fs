# File Research: sources/os/bsd/netbsd-src/sys/sys/container_of.h

Provides type-checked `container_of` and `const_container_of` macros for recovering an enclosing structure from an embedded field pointer.

Key content:
- Includes `<sys/stddef.h>` for `offsetof`.
- Validation macros compare the supplied pointer type with the target field type through a zero-sized arithmetic expression.
- Coverity/LGTM builds skip validation to avoid analyzer warnings.

Important behavior:
- `container_of(PTR, TYPE, FIELD)` subtracts `offsetof(TYPE, FIELD)` from `PTR`.
- `const_container_of` preserves constness.
- The validation expression is compile-time only and should not affect generated code.
