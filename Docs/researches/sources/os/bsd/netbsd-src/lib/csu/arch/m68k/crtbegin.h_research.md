# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/m68k/crtbegin.h

m68k `crtbegin` architecture header. It injects calls to `__do_global_ctors_aux` and `__do_global_dtors_aux` into `.init` and `.fini`.

The assembly selects `bsrl` for PIC and `jsr` for non-PIC builds.
