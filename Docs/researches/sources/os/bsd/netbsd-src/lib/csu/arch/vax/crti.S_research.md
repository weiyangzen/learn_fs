# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/vax/crti.S

VAX `crti` fragment. It includes `sysident.S` and defines `_init` and `_fini`.

Each function begins with `.word 0`, the VAX procedure entry mask.
