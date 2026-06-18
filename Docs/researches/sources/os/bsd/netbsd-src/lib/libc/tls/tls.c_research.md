# File Research: sources/os/bsd/netbsd-src/lib/libc/tls/tls.c

## Purpose
Provides libc-side static TLS setup and fallback runtime-loader TLS allocation/free routines for architectures using TLS variant I or II.

## Main Entry Points
- `__libc_static_tls_setup()` scans program headers, skips dynamic executables, allocates a TLS block/TCB, and installs the TCB with `__lwp_settcb()` or `_lwp_setprivate()`.
- `_rtld_tls_allocate()` allocates TLS storage for the initial thread via `mmap()` and later threads via `calloc()`, lays out variant-I or variant-II TCB/TLS memory, and copies the TLS init image.
- `_rtld_tls_free()` frees TLS storage with `munmap()` for the initial thread block or `free()` for later allocations.
- `__libc_tls_get_addr()` is a weak TLS lookup stub that aborts.

## Control Flow
`dl_iterate_phdr()` invokes `__libc_static_tls_setup_cb()`, which detects `PT_INTERP` to avoid static setup for dynamic programs and records the `PT_TLS` image address, file size, memory size, and alignment. Static setup allocates a TCB only when no interpreter is present.

## Dependencies
Depends on ELF program header iteration, `struct tls_tcb`, TLS variant macros, mmap/calloc/free, LWP private pointer APIs, and libc namespace/weak alias machinery.

## Risks And Notes
Allocation failure exits the process with status 127 using direct `write()`/`_exit()`, avoiding malloc-dependent error handling. Layout is ABI-sensitive: variant I places the TCB before TLS data, while variant II places it after a rounded TLS allocation.
