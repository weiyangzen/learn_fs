# File Research: sources/os/bsd/dragonflybsd/sys/sys/stdint.h

This header is a kernel proxy for fixed-width integer, boolean, max-width, pointer, and offset types, while forwarding userland to standard `<stdint.h>`.

Key responsibilities:
- Includes `sys/cdefs.h` and `machine/stdint.h`.
- Documents that userland should use `<stdint.h>` instead.
- In kernel builds:
  - includes machine integer limits
  - defines `boolean_t`
  - defines `bool`, `true`, and `false` when C/C++ conditions permit
  - defines `offsetof`
  - defines `ptrdiff_t`
  - defines signed fixed-width types `int8_t`, `int16_t`, `int32_t`, `int64_t`
  - defines unsigned fixed-width types with declaration guards
  - defines `intptr_t` and `uintptr_t`
  - defines `intmax_t` and `uintmax_t`
- In non-kernel builds, includes `<stdint.h>` if needed.

Important invariants:
- Kernel `boolean_t` is `_Bool` for C99/GCC-capable environments and `int` otherwise.
- Userland inclusion is tolerated but delegated to the normal userland `<stdint.h>`.
- The header explicitly warns it is not a placeholder for non-integer types.

Research notes:
- This file bridges kernel headers that need C99 integer types without exposing the full userland stdint implementation path.
