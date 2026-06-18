# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/alpha/Makefile.inc

Alpha CSU make include. It adds the architecture include directory and defines `ELFSIZE=64`.

This allows the common CSU code and ELF note generation to use 64-bit Alpha ELF layouts.
