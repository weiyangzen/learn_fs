# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/sscanf.c

Implements `sscanf()` and `sscanf_l()` as variadic wrappers over `vsscanf()` and `vsscanf_l()`. It does not build a fake stream itself in this file.

The locale-specific public symbol has a weak alias to `_sscanf_l`.
