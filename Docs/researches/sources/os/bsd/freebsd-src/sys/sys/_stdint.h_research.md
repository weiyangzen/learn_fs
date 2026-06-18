# File Research: sources/os/bsd/freebsd-src/sys/sys/_stdint.h

Standard fixed-width integer typedef layer.

Key elements:
- Defines `int8_t` through `int64_t`, `uint8_t` through `uint64_t`, `intptr_t`, `uintptr_t`, `intmax_t`, and `uintmax_t`.
- Under BSD visibility, defines `int64ptr_t` and `uint64ptr_t`.

Dependencies:
- Uses internal `__*` integer types from `sys/_types.h` or surrounding include context.

Research notes:
- Provides public names while guarding each typedef with `_DECLARED` macros.
- Pointer-width compatibility typedefs are useful for 32/64-bit ABI translation.
