# File Research: sources/os/bsd/freebsd-src/sys/sys/_decls.h

C/C++ linkage helper header.

Defines:
- `__BEGIN_DECLS` as `extern "C" {` under C++ and empty under C.
- `__END_DECLS` as `}` under C++ and empty under C.

Research relevance:
- Common public header utility for making C declarations safe in C++ translation units.
