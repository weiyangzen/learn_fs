# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/swscanf.c

Implements `swscanf()` and `swscanf_l()` as variadic wrappers over `vswscanf()` and `vswscanf_l()`. The actual wide string scanning is delegated elsewhere.

The locale variant is weak-aliased as `swscanf_l -> _swscanf_l`.
