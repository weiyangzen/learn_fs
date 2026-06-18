# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/sparc/crt0.S

SPARC process entry stub. It clears `%fp`, aligns and expands the stack to a standard frame, moves cleanup from `%g3` to `%o0`, and passes `ps_strings` from `%g1` to `%o1`.

It then calls common `___start`.
