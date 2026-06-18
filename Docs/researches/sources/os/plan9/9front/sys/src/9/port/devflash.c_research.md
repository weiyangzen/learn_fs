# File Research: sources/os/plan9/9front/sys/src/9/port/devflash.c

Purpose: flash memory device `#F`, abstracting architecture flash banks and registered flash chip drivers.

Exposed interface: `#F[bank]/flash[bank]/` with partition data files and `<partition>ctl` files. Initial partition is `flash` covering the full bank. Control commands include `erase`, `add`, `remove` placeholder, `sync` placeholder, and `protectboot`.

Core implementation: `addflashcard` registers chip-type reset handlers. `flashreset` asks the architecture for bank mappings, finds a matching flash type, resets it, enables boot protection, and creates the full-bank partition. `flashgen`/`flash2gen` synthesize partition and ctl entries.

I/O paths: `flashread` reads partition data or emits ctl information including chip id, width, sort, regions, erase size, and page size. `flashwrite` writes partition data, erases blocks/all, adds partitions, and toggles boot protection. `readflash`, `writeflash`, and `eraseflash` serialize with the flash qlock, handle device width/alignment, call chip callbacks, and toggle architecture write protection.

Dependencies: `flashif.h`, architecture hooks `archflashreset` and `archflashwp`, and chip-specific flash drivers.

Research notes: critical areas are erase-block alignment, boot-region protection, partition bounds, width/interleave handling, and the placeholders for remove/sync commands.
