# File Research: sources/os/plan9/9front/sys/src/9/port/sdnvme.c

Plan 9 `SDifc` block driver for PCI NVMe controllers.

Key responsibilities:
- Discovers PCI NVMe controllers by class code, maps BAR0 registers, validates NVM command-set support, and chooses a controller memory page size.
- Builds admin and I/O submission/completion queues, including one shared completion queue and per-CPU submission queues when possible.
- Issues NVMe commands through `qcmd()`/`wcmd()`, waits through per-command `WS` records, and completes them from `nvmeintr()`.
- Implements block reads/writes in `nvmebio()` using NVMe read/write opcodes and splits transfers around PRP/page constraints.
- Presents NVMe namespaces as Plan 9 `sd` units, faking enough SCSI inquiry/read-write behavior for the shared disk stack.
- Identifies controller and namespace data, fills unit geometry, model, serial, firmware, and namespace sector size.
- Adds a per-unit `smart` file that fetches and formats NVMe SMART / health log page data.

Dependencies:
- Uses Plan 9 kernel PCI, interrupt, DMA, rendezvous, and `sd` infrastructure.
- Calls shared SCSI emulation helpers `sdfakescsi()` and `sdfakescsirw()`.
- Uses `mallocalign`, `dmaflush`, `PCIWADDR`, `intrenable`, `pcisetbme`, and `vmap`.

Notable behavior:
- Admin commands serialize through the controller `QLock`; I/O commands choose a queue by `m->machno % ctlr->nsq`.
- Interrupts mask enabled completion vectors while processing and unmask afterward.
- Namespace list fallback assumes namespace `1` if namespace-list identify fails.
- Disable path requests normal shutdown, disables the controller, tears down interrupts/DMA, and frees queues plus identify buffers.

Research notes:
- The driver supports only simple PRP use: first PRP plus optional second PRP, so `nvmebio()` limits chunk size to fit that model.
- `readsmart()` prints 64-bit counters using the low 64 bits of NVMe 128-bit SMART fields.
