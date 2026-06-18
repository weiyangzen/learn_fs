# File Research: sources/os/bsd/netbsd-src/lib/libc/include/port_before.h

ISC porting pre-include header.

Provides:
- `namespace.h` inclusion.
- `ISC_FORMAT_PRINTF(a,b)` mapped to compiler printf-format attribute.
- `ISC_SOCKLEN_T socklen_t`.
- `DE_CONST(c,v)` using `__UNCONST` on NetBSD or a portable strchr trick otherwise.
- `UNUSED(a)` macro, with lint-specific behavior.

Used before imported ISC source includes.
