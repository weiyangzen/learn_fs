# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/sparc/crtbegin.h

SPARC `crtbegin` header. It injects calls to constructor and destructor helpers into `.init` and `.fini`.

Each call is followed by a `nop`, matching SPARC delay-slot requirements.
