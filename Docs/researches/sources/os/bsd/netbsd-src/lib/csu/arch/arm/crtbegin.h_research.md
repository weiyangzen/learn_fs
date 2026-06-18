# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/arm/crtbegin.h

ARM `crtbegin` architecture header. It injects calls to `__do_global_ctors_aux` into `.init` and `__do_global_dtors_aux` into `.fini`.

This is for non-array ARM configurations; AAPCS configurations define `HAVE_INITFINI_ARRAY` elsewhere.
