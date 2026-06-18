# File Research: sources/os/bsd/netbsd-src/lib/libc/dlfcn/Makefile.inc

Build fragment for libc `dlfcn` support. It adds include paths for `libexec/ld.elf_so` and the local `dlfcn` directory, and appends `dlfcn_elf.c` to `SRCS`.

Dependencies: requires dynamic linker headers, especially `rtld.h`, for shared structure and auxiliary-vector declarations.

Risks/invariants: libc's fallback `dlfcn` stubs must stay ABI-compatible with runtime linker implementations that override them.
