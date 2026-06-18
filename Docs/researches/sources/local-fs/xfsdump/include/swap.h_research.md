# File Research: sources/local-fs/xfsdump/include/swap.h

`swap.h` builds higher-level integer conversion macros on top of `swab.h`.

Key behavior:
- Includes `<xfs/xfs.h>` and `<swab.h>`.
- Detects big-endian hosts as `XFS_NATIVE_HOST`.
- Defines `ARCH_NOCONVERT` as native/no-conversion and `ARCH_CONVERT` as either no-convert on big-endian or convert on little-endian.
- Provides `INT_SWAP16`, `INT_SWAP32`, and `INT_SWAP64` unless `HAVE_SWABMACROS` supplies alternatives.
- `INT_SWAP(type, var)` chooses swap width by `sizeof(type)`.
- `INT_GET(ref, arch)` reads either directly or byte-swapped.
- `INT_SET(ref, arch, valueref)` writes either directly or byte-swapped, with a constant-value optimization.
- `INT_XLATE(buf, p, dir, arch)` abstracts decode vs encode direction.

Role:
- Used by architecture translation helpers to read/write on-media xfsdump structures consistently across host byte order.
