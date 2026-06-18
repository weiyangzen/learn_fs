# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/riscv/sys/compat_Ovfork.S

Defines RISC-V compatibility `vfork`.

The file is public-domain and maps `vfork` to `__vfork14` while emitting a warning for old references.

This is a simple syscall alias veneer.
