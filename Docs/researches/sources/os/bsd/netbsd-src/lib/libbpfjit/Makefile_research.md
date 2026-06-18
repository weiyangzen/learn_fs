# File Research: sources/os/bsd/netbsd-src/lib/libbpfjit/Makefile

Builds the private BPF JIT library.

Key behavior:
- Declares `LIB=bpfjit` and `LIBISPRIVATE=yes`.
- Does not install a manpage.
- Builds `bpfjit.c` from `${NETBSDSRCDIR}/sys/net`.
- Adds include path to the in-tree SLJIT source directory.
- Uses `WARNS=4`.

Dependencies:
- Kernel BPF JIT source and private SLJIT distribution.
