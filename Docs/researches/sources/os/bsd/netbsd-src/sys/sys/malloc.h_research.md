# File Research: sources/os/bsd/netbsd-src/sys/sys/malloc.h

Kernel compatibility wrapper for traditional BSD `malloc/free/realloc`. It defines `M_WAITOK`, `M_NOWAIT`, and `M_ZERO`, includes `mallocvar.h`, declares `kern_malloc`, `kern_realloc`, and `kern_free`, and maps the old typed allocator macros to the modern untyped functions.

It preserves old source patterns while allocation types are currently diagnostic stubs. Risks are sleeping allocation in invalid contexts and legacy code assuming type-specific accounting that this header no longer provides.
