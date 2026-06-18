# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/hppa/string/ffs.S

This HPPA `ffs` implementation returns zero for an input of zero, otherwise computes the position of the least significant set bit using staged low-half tests and shifts. Its comments describe bit positions as 32 down to 1 in VAX-style numbering.
