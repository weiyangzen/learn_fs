# File Research: sources/os/plan9/plan9/sys/src/9/omap/io.h

Defines the OMAP General-Purpose Memory Controller register layout and bit fields for flash/non-DRAM memory.

Key points:
- Describes GPMC as working only with flash memory in this port.
- Defines system config bits for idle control and posted NAND writes.
- Defines chip-select config register indices for signal control and address map config.
- Defines chip-select control bits for muxed address/data, NOR/NAND device type, 8/16-bit device size, and sync read/write.
- Defines chip-select map bits for valid mapping and 16MB/128MB size encodings.
- Defines `Gpmc` register layout: sysconfig/status/IRQ, timeout/error/config/status, eight chip-select blocks, prefetch controls, ECC registers, BCH result registers, and BCH software data.
- Each chip-select block includes seven config registers plus NAND command/address/data registers.

Dependencies and interactions:
- Included by OMAP platform files that need GPMC/flash definitions.
- `archomap.c` configures GPMC-related pad modes and flash reset uses `PHYSNAND`.
- Flash drivers can use this structure for OneNAND/NAND access.

Research relevance:
- Hardware register definition header for OMAP flash memory controller support.
