# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/m68k/sys/compat_sigprocmask.S

Implements m68k compatibility `sigprocmask` for the NetBSD 1.3 signal-mask ABI. It warns about compatibility references.

If the new mask pointer is null, it changes the operation to `SIG_BLOCK` with an empty mask; otherwise it dereferences the pointed-to old mask and passes the integer mask to `compat_13_sigprocmask13`.

On success it stores the returned old mask through the optional old-mask pointer, then returns zero.
