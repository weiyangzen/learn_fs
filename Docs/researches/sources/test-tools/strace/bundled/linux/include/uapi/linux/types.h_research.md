# sources/test-tools/strace/bundled/linux/include/uapi/linux/types.h

## Purpose

Defines Linux-specific fixed-width, endian-tagged, checksum, aligned, and poll types that form the foundation for most UAPI structs in this group. strace's bundled headers depend on these typedefs for ABI-correct structure layouts.

## Important APIs, Types, and Dependencies

The header includes `asm/types.h`, and outside assembly includes `linux/posix_types.h`. If the compiler supports `__int128`, it defines aligned `__s128` and `__u128`. It defines sparse-aware `__bitwise` and legacy `__bitwise__`, endian-tagged typedefs `__le16`, `__be16`, `__le32`, `__be32`, `__le64`, `__be64`, checksum types `__sum16` and `__wsum`, aligned macros `__aligned_u64`, `__aligned_s64`, `__aligned_be64`, `__aligned_le64`, and `__poll_t`.

## Control Flow, State, and Integration

This is a type foundation header with no runtime flow or persistent state. Its integration point is structural ABI stability: fields using aligned 64-bit macros must have the same layout for 32-bit userspace talking to 64-bit kernels.

## Risks and Test Signals

Risks include removing sparse annotations, using plain `__u64` where an aligned type is required, and breaking 32/64-bit compat layout. Test signals are compile checks for all dependent headers, `sizeof`/`offsetof` validation on compat-sensitive structs, and endian-tagged type availability.
