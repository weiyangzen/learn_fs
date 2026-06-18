# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/powerpc/crtbegin.h

PowerPC `crtbegin` architecture header. It injects `bl __do_global_ctors_aux` into `.init` and `bl __do_global_dtors_aux` into `.fini`.

This connects the common constructor/destructor helpers to legacy init/fini sections.
