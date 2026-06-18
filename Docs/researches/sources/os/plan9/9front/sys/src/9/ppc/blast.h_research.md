# File Research: sources/os/plan9/9front/sys/src/9/ppc/blast.h

Board-specific constants for the PowerPC Blast board.

Key responsibilities:
- Defines input clock speed, physical memory/chip-select layout for flash, DSPs, SDRAM, FPGA, and optional EEPROM.
- Defines the flash location of `plan9.ini`, TLB entry count, and kernel PTE policy bits.
- Defines SMC UART pin configuration and FCC Ethernet signal/pin masks for three FCC ports.

Dependencies:
- Included by `mem.h` when not building the UCU/Saturn configuration.

Notable behavior:
- Sets `MEM2SIZE` to zero in the active configuration despite documenting local-bus SDRAM ranges.
