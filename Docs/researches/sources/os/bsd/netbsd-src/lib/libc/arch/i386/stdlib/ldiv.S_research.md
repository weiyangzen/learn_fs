# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/i386/stdlib/ldiv.S

This i386 `ldiv` implementation mirrors `div.S` for long operands: it uses `cdq`/`idiv`, stores quotient and remainder into the caller-supplied result object, and returns that object pointer.
