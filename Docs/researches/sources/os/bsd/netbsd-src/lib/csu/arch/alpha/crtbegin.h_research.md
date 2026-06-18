# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/alpha/crtbegin.h

Alpha `crtbegin` architecture header. It injects assembly into `.init` and `.fini` to reload the global pointer and call `__do_global_ctors_aux` / `__do_global_dtors_aux`.

The design assumes GP reload is necessary around constructor/destructor helper calls.
