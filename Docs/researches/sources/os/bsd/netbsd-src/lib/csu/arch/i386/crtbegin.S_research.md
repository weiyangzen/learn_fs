# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/i386/crtbegin.S

i386 hand-written `crtbegin` implementation. It defines legacy `.ctors`, `.dtors`, `.eh_frame`, `.jcr`, `__dso_handle`, initialization flags, and weak references for `__cxa_finalize`, frame registration, and Java class registration.

It implements `__do_global_ctors_aux` and `__do_global_dtors_aux` in PIC-aware assembly using `%ebx` as GOT base, then wires those helpers into `.init` and `.fini`.
