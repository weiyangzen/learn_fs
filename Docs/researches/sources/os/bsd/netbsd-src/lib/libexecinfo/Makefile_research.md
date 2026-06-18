# File Research: sources/os/bsd/netbsd-src/lib/libexecinfo/Makefile

## Purpose
Build description for NetBSD `libexecinfo`.

## Main Content
- Builds `LIB=execinfo` and installs `execinfo.h` into `/usr/include`.
- Always builds `symtab.c` and `backtrace.c`.
- Uses libelf through `LIBDPLIBS`.
- Builds `unwind.c` by default when `USE_UNWIND=yes`; otherwise uses `builtin.c`.
- Adds `unwind_arm_ehabi_stub.c` for earm ARM targets.
- Includes machine-specific `symbol_${LIBEXECINFO_MACHINE_ARCH}.c` and export symbols when present.
- Generates merged `execinfo.expsym` from common and machine-specific symbol lists.
- Installs manual-page links for backtrace symbol APIs.

## Integration
Part of NetBSD userland library build system via `<bsd.lib.mk>`.

## Risks / Notes
The selected backtrace implementation depends on `USE_UNWIND` and target architecture; exported symbol set is generated at build time.
