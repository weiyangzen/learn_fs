# File Research: sources/os/plan9/plan9/sys/src/9/port/devflash.c

Implements `#F`, a flash memory device with up to two banks. Each detected bank exposes a `flash` directory with partition data files and matching `<name>ctl` files.

Flash cards are discovered in `flashreset` through `archflashreset`, matched against registered `Flashtype` drivers from `addflashcard`, reset by the card driver, and initially partitioned as a single `flash` partition spanning the full device. Each `Flash` has regions, erase sizes, width/interleave details, optional read/write/erase callbacks, and write-protect hooks.

Data reads and writes are constrained to partition bounds and translated to absolute flash offsets. `readflash` handles aligned and partial-width reads, using card callbacks when present or memory-mapped access otherwise. `writeflash` performs read-modify-write for unaligned spans, toggles hardware write protect, and refuses writes to protected boot regions. `eraseflash` similarly enforces boot protection and calls region or whole-chip erase operations.

Ctl reads report flash id, device id, width, sort, and overlapping erase/page regions. Ctl writes support `erase`, `add`, `remove` placeholder, `sync` placeholder, and `protectboot [off]`. `add` creates a new named partition within the current partition, validating erase-unit alignment through `flashaddr`.

This file abstracts NOR-style flash geometry and partition management over architecture/card-specific low-level routines. Important edge cases are erase alignment, partial-width writes, and boot-region protection.
