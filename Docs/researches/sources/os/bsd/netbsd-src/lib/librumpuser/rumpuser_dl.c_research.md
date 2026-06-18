# File Research: sources/os/bsd/netbsd-src/lib/librumpuser/rumpuser_dl.c

## Summary
Bootstraps dynamically linked rump modules, components, event counters, sysctl setup functions, and kernel symbol tables.

## Key Details
- Compiles the main implementation only for ELF systems with `HAVE_DLINFO`; otherwise `rumpuser_dl_bootstrap` is a no-op.
- Uses `dlopen(NULL)` and `dlinfo(..., RTLD_DI_LINKMAP, ...)` to inspect the dynamic linker link map.
- Handles static-link heuristics by returning when no useful dynamic link map exists.
- Walks objects last-to-first to process likely dependencies before dependents.
- Collects ELF symbol and string tables from `librump*` objects and the main object, accepting symbols beginning with `rump`, `RUMP`, or `__`.
- Supports ELF32/ELF64 through accessor macros, and supports both SysV `DT_HASH` and GNU `DT_GNU_HASH` symbol counts.
- Adjusts dynamic-section pointers differently for glibc, Solaris, DragonFly, FreeBSD, NetBSD, musl-like systems, and MIPS exceptions.
- Processes link sets for modules, rump components, sysctl functions, and event counters via `dlsym` start/stop symbols.

## Notes
The symbol table is rebuilt into contiguous malloc-backed buffers before being handed to the rump kernel through `symload`.
