# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/sparc64/crtbegin.h

SPARC64 `crtbegin` header. It injects calls to `__do_global_ctors_aux` and `__do_global_dtors_aux` into `.init` and `.fini`.

The code mirrors the SPARC 32-bit helper pattern with SPARC64 syntax.
