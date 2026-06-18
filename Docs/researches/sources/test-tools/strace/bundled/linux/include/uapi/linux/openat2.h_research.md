# sources/test-tools/strace/bundled/linux/include/uapi/linux/openat2.h

## Purpose

Defines the `openat2(2)` argument ABI. strace uses it to decode the `struct open_how` payload and the `RESOLVE_*` path-resolution constraints that distinguish `openat2` from older `openat` behavior.

## Important APIs, Types, and Dependencies

The only dependency is `linux/types.h`. `struct open_how` contains `flags`, `mode`, and `resolve`, all `__u64` for extensible syscall ABI stability. The exported resolve bits are `RESOLVE_NO_XDEV`, `RESOLVE_NO_MAGICLINKS`, `RESOLVE_NO_SYMLINKS`, `RESOLVE_BENEATH`, `RESOLVE_IN_ROOT`, and `RESOLVE_CACHED`.

## Control Flow, State, and Integration

The header has no runtime control flow. Its values are consumed by the kernel during pathname lookup and by strace when formatting the third syscall argument. Kernel state affected by callers is the opened file descriptor and path walk result; the header itself only specifies validation rules such as rejecting unknown `flags` bits and requiring `mode` to be zero unless creation flags are set.

## Risks and Test Signals

Risks include silently accepting unknown flag bits in user decoders, confusing `RESOLVE_BENEATH` with `RESOLVE_IN_ROOT`, and missing `RESOLVE_CACHED` retry behavior where `-EAGAIN` is a valid outcome. Test signals are syscall decode tests that show all `open_how` fields, named resolve flags, unknown-bit fallback, and correct handling of short or future-extended struct sizes.
