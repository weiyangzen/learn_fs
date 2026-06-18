# File Research: sources/os/bsd/netbsd-src/lib/libc/include/__sysctl.h

Private libc declaration for raw `__sysctl`.

Purpose:
- Declares syscall stub `int __sysctl(const int *, unsigned, void *, size_t *, const void *, size_t);`.
- Notes it bypasses higher-level library wrapper handling such as `user.*` nodes.
- Used by the sysctl wrapper, stack protector setup for `kern.arandom`, and runtime linker ld.so.conf interpretation.
