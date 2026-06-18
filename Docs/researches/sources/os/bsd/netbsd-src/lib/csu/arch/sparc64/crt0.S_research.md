# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/sparc64/crt0.S

SPARC64 process entry stub. It clears `%fp`, clears `%g4` for memory model data base use, moves cleanup from `%g3` to `%o0`, and passes `ps_strings` from `%g1` to `%o1`.

It branches predict-taken to common `___start`.
