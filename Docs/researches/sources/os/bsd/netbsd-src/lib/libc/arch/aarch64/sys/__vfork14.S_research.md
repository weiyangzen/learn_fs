# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/aarch64/sys/__vfork14.S

AArch64 wrapper for versioned `vfork`.

Key behavior:
- Saves link register in `x8`.
- Calls `SYSTRAP(__vfork14)` and error handling.
- Uses fork-style `x1` return discriminator to return zero in the child and the child pid in the parent.
- Returns via saved `x8`.

Dependencies:
- Kernel fork/vfork return convention.
