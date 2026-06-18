# File Research: sources/os/bsd/netbsd-src/lib/libarch/alpha/alpha_pci_io.c

Alpha PCI/EISA/ISA programmed-I/O helper code. It enables I/O by retrieving and mapping PCI I/O bus windows, then selects either BWX byte/word-capable operations or swizzled 32-bit operations based on window flags.

The swizzled path computes port addresses with bus offset, address shift, and size shift, then extracts/inserts byte or word values from 32-bit ports. The BWX path uses Alpha byte/word load/store helpers. All I/O operations use `alpha_mb()` barriers, and missing windows are treated as fatal via `warnx` and `abort`.
