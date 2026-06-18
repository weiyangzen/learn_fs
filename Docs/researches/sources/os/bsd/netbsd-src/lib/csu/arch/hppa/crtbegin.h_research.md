# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/hppa/crtbegin.h

HPPA `crtbegin` architecture header. It injects branch-and-link calls to `__do_global_ctors_aux` and `__do_global_dtors_aux` into `.init` and `.fini`.

Each injected call uses `%rp` and a following `nop`, matching HPPA calling conventions.
