# File Research: sources/os/bsd/freebsd-src/sys/sys/stdatomic.h

## Purpose
`stdatomic.h` implements the C11 atomic API for FreeBSD across Clang C11 atomics, GCC `__atomic` builtins, and older GCC `__sync` builtins.

## Main Interfaces
- Defines lock-free macros when compiler-provided values exist.
- Defines `memory_order` values, `atomic_thread_fence()`, and `atomic_signal_fence()`.
- Declares atomic integer typedefs for bool, char, short, int, long, long long, C23 char8, char16, char32, wchar, least/fast widths, intptr, uintptr, size, ptrdiff, intmax, and uintmax.
- Provides explicit atomic operations for compare-exchange, exchange, fetch add/sub/and/or/xor, load, and store.
- Provides non-kernel default seq-cst convenience macros and `atomic_flag` operations.

## Implementation Notes
Kernel builds treat atomics as always lock-free and intentionally omit the non-explicit convenience operations to encourage explicit memory ordering. The fallback `__sync` path wraps values in `.__val` and uses full-barrier or compatibility primitives.

## Dependencies and Constraints
Includes `sys/cdefs.h` and `sys/_types.h`. Unsupported compilers fail with a preprocessor error. C++ builds temporarily map `_Bool` to `bool` if needed.
