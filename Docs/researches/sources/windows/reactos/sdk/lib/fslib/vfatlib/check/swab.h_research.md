# File Research: sources/windows/reactos/sdk/lib/fslib/vfatlib/check/swab.h

Imported Linux byte-swap helper header for endian conversion support.

Key elements:
- Defines raw constant/runtime byte swaps for 16-, 32-, and optionally 64-bit integer types.
- Provides architecture override hooks such as `__arch__swab16`.
- Uses GCC constant-folding when available.
- Exposes kernel-style aliases only under `__KERNEL__`.

Dependencies:
- Includes `compiler.h` and expects Linux-style `__u16`, `__u32`, `__u64`, and attribute macros.

Research notes:
- This is compatibility infrastructure, not FAT-specific logic.
- In this ReactOS subtree it supports byteorder headers used by the checker port on relevant architectures.
