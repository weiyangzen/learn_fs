# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/ia64/crtbegin.h

IA-64 `crtbegin` architecture header. It injects `.init` and `.fini` calls to `__do_global_ctors_aux` and `__do_global_dtors_aux`.

The injected calls use IA-64 branch-call syntax with `b0`.
