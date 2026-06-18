# File Research: sources/windows/reactos/sdk/lib/fslib/ext2lib/types.h

This tiny header supplies Linux-style integer aliases used by `ext2_fs.h`.

Contents:
- `__u32`, `__s32`, `__u16`, `__s16`, and `__u8` typedefs mapped to C integer types.

Risk points:
- Types assume Windows/ReactOS ABI widths where `unsigned long` is 32-bit.
- No 64-bit aliases are provided because the included ext2 structures in this group do not need them.
