# File Research: sources/os/plan9/9front/sys/src/9/pc/yukdump.h

Debug dump helpers and register tables for a Yukon/Marvell-style Ethernet driver.

Key contents:
- Defines `Regdump` descriptors with register offset, width, and display name.
- Provides register descriptor arrays for PCI registers, GMAC registers, MAC registers, and general device registers.
- `dumppci`, `dumpgmac`, `dumpmac`, and `dumpreg` format hardware register snapshots into a buffer using controller-specific read helpers.
- `optab` and `rs` map descriptor operation codes to short strings.
- `dumpring` summarizes populated ranges in a block ring.
- `descriptorfu` prints detailed transmit/receive descriptor state around the hardware get index for debugging.

Notable dependencies:
- Requires the including Yukon driver to define `Ctlr`, ring types, descriptor/status layouts, register constants, and helper functions such as `gmacread`, `macread32`, `prread16`, and `Pciwaddrl`.

Research notes:
- This is a header containing debug code, not only declarations.
- It is intentionally coupled to one driver’s private data structures and is not a general register-dump facility.
