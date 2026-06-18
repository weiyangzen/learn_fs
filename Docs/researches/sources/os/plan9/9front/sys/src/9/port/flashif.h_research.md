# File Research: sources/os/plan9/9front/sys/src/9/port/flashif.h

Shared flash-memory driver interface for NOR, NAND, serial flash, and logical flash partitions.

Key contents:
- Defines `Flashpart` for up to 8 logical partitions.
- Defines `Flashregion` for erase-block regions, including erase/page size shifts and spare bytes for ECC.
- Defines `Flashchip` for physical chip geometry, IDs, interleave width, CFI algorithm, and protection state.
- Defines the main `Flash` object with a `QLock`, type/address/size fields, reset hooks, erase/read/write/suspend/resume/attach callbacks, geometry, partitions, and private driver data.
- Declares registration, architecture reset/write-protect, generic flash access, and architecture NAND access routines.

Role:
- Provides the contract between `devflash`, flash-type drivers, and architecture-specific glue.
- Carries both bus-level geometry and flash-operation callback tables.

Notable constraints:
- Region and partition counts are fixed-size arrays.
- NAND operations are intentionally split into architecture callbacks for CLE/ALE, claim/power, byte write, and byte read.
