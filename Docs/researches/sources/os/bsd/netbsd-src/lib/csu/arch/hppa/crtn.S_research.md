# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/hppa/crtn.S

HPPA `crtn` fragment. It defines matching section epilogues for `.init` and `.fini`.

The epilogue restores `%rp`, stack pointer, and `%r3`, then returns through `%rp`.
