# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/mips/crt0.S

MIPS process entry stub. It documents the NetBSD register ABI, sets up GP, moves cleanup from `a1` to `a0`, moves `ps_strings` from `a3` to `a1`, and jumps through the GOT-resolved `___start`.

The code uses `R_MIPS_JALR` relocation annotation for the indirect branch.
