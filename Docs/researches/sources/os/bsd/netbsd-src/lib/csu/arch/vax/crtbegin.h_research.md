# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/vax/crtbegin.h

VAX `crtbegin` header. It injects calls to `__do_global_ctors_aux` and `__do_global_dtors_aux` into `.init` and `.fini`.

This header is present even though VAX also has an assembly `crtbegin.S`; the build selects the assembly file when present.
