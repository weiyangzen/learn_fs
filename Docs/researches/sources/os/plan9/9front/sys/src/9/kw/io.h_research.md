# File Research: sources/os/plan9/9front/sys/src/9/kw/io.h

Kirkwood I/O and SoC register definition header. It defines bus types, PCI BDF helpers, internal register base addresses, SoC revision constants, interrupt vector numbers, interrupt controller register structures, CPU control/status registers, DRAM/window target attributes, and PCIe register layout.

Important hardware mappings include eFuse, PCI/PCIe config space, MPP, SDIO, interrupt banks, bridge interrupts, CPU reset/clock/L2 registers, and the Marvell PCIe capability/configuration block. It also defines DRAM target/attribute constants used by Ethernet and USB bridge address windows.

This file is consumed by platform drivers such as Ethernet, EHCI, UART, trap/interrupt code, and architecture reset/setup code.

Notable risks: several declarations are partial hardware maps with comments saying "some day" or "if we actually use these"; register offsets must match the Marvell 88F6281/Kirkwood manuals.
