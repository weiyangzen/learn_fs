# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/include/setjmp.h

Declares old setjmp/longjmp compatibility entry points.

It exposes `__setjmp14`, `__longjmp14`, `__sigsetjmp14`, and `__siglongjmp14` with `__returns_twice` / `__dead` attributes.

This preserves old nonlocal-jump ABI.
