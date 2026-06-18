# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/vax/sys/compat_Ovfork.S

Implements VAX compatibility `vfork`.

It uses a VAX-specific stack/return-address trick: saves the caller return address, rewrites the frame return address to a local label, returns before issuing `chmk $SYS_vfork`, then jumps indirectly through the saved return address. Child/parent return values are fixed with `mnegl` and `bicl2`.

The error path handles both reentrant and non-reentrant errno storage.
