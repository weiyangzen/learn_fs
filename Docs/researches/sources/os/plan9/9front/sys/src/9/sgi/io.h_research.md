# File Research: sources/os/plan9/9front/sys/src/9/sgi/io.h

Defines SGI I/O constants: `Mhz`, uncached MMIO mapping macro `IO(t,x)`, SGI IRQ numbers, INT2 local interrupt register addresses, and key device bases for HPC3 Ethernet, keyboard/mouse, Newport graphics, and memory configuration registers.

`INT2_BASE` is fixed to the IP24/Indy address. The file is included by SGI device, interrupt, and memory discovery code.
