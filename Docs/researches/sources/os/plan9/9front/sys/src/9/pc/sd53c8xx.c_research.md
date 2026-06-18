# File Research: sources/os/plan9/9front/sys/src/9/pc/sd53c8xx.c

Implements a Plan 9 SCSI disk interface driver for NCR/Symbios/LSI Logic 53c8xx PCI SCSI controllers.

Key behavior:
- Defines controller register layout (`Ncr`), DMA/script data structures (`Dsa`, `Movedata`), negotiation state, chip feature flags, burst encodings, and supported chip variants.
- Includes generated SCRIPTS microcode from `sd53c8xx.i` and patches it through `na_fixup()` using physical script/register addresses and DSA offsets.
- `sd53c8xxpnp()` scans PCI vendor `0x1000`, matches supported chip variants, maps register BARs with `vmap()`, uses local RAM for scripts when available, otherwise allocates host memory, initializes the DSA sentinel list, and creates `SDev` instances.
- `sd53c8xxenable()` enables bus mastering, initializes sync timing tables, records BIOS setup, resets the bus, and registers interrupts.
- `synctabinit()`, `chooserate()`, `setsync()`, `setasync()`, and `setwide()` implement wide/synchronous transfer negotiation.
- `sd53c8xxinterrupt()` handles script interrupts, DMA interrupts, SCSI interrupts, reselection, phase mismatch, parity, timeout, unexpected disconnect, illegal instruction, bus fault, and many script diagnostic events.
- Read/write phase mismatch recovery accounts for DMA FIFO and SCSI FIFO residues, advances transfer descriptors, and restarts scripts at recovery labels.
- `sd53c8xxrio()` is the main SCSI request path: allocates a DSA, serializes per target, builds identify/WDTR/SDTR messages, sets command/data/status move descriptors, starts or signals the script engine, waits up to 600 seconds, handles check condition by issuing request sense, computes residual length, and frees the DSA.

Research notes:
- Filesystem relevance is direct: this is a block-storage path exposed through `SDifc`, using `scsibio` for block I/O.
- The code is tightly coupled to 32-bit DMA address assumptions via `PCIWADDR`, `PCIWINDOW`, and `KADDR`.
- There is extensive recovery logic for hardware/script edge cases, especially phase mismatches and residual accounting.
- Known-problem comments mention possible read/write mismatch recovery failure on 53c1010.
