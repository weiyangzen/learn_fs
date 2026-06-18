# File Research: sources/os/plan9/9front/sys/src/9/pc/sdiahci.c

Implements an AHCI SATA/ATAPI storage driver for Intel/AMD and related PCI AHCI controllers.

Key behavior:
- Defines controller and drive limits, controller families, drive states, SATA modes, debug flags, and runtime structures for `Ctlr` and `Drive`.
- `iapnp()` scans PCI devices, identifies AHCI-capable controllers by vendor/device/class, maps AHCI BARs with `vmap()`, performs BIOS handoff, applies Intel/AMD setup quirks, initializes HBA state, maps implemented ports to `Drive` objects, configures ports, initializes enclosure LEDs, and registers `SDev`s.
- `iaenable()` registers controller interrupts, enables HBA interrupts, and starts background kernel processes for drive polling and LED updates.
- Port setup uses `ahciconfigdrive()`, `setupfis()`, command-list/table allocation, FIS receive area setup, COMRESET, power/spin-up handling, interrupt enables, and command engine start.
- Drive state machine uses `updatedrive()`, `configdrive()`, `resetdisk()`, `newdrive()`, `checkdrive()`, and `satakproc()` to handle hotplug, PHY changes, errors, resets, slow initialization, retries, and hung commands.
- ATA identify and setup flow uses AHCI command FIS helpers from `fis.h`/`ahci.h`, sets transfer mode, disables APM when supported, and extracts model/firmware/serial/WWN/sector size.
- I/O path:
  - `ahcibio()` handles block reads/writes in chunks, with larger chunks for LBA48 and controller-specific limits.
  - `iario()` handles SCSI emulation, flush cache, and regular disk requests.
  - `iariopkt()` handles ATAPI packet requests.
  - `iaataio()` handles raw ATA/FIS protocol requests with sanitization.
- LED/enclosure support implements IBPI-style blinking through AHCI enclosure management or ESB-specific registers.
- Control/status paths expose per-drive and top-level status, modes, flags, registers, geometry, alignment, missed IRQs, debug toggles, forced state, forced mode, and transfer mode.

Research notes:
- Filesystem relevance is direct: this is a primary SATA block-device backend for Plan 9’s `sd` layer.
- It supports SATA disks and ATAPI devices, hotplug, cache flush, raw ATA, and SCSI-compatible block I/O.
- Error handling is state-machine driven: failed commands may return retry/check/eio, trigger software reset, disable DMA for hung devices, or move the drive into reset/portreset/offline states.
- It depends heavily on PCI enumeration, MMIO mapping, interrupt routing, DMA-accessible command structures, AHCI register definitions, and Plan 9 `SDifc`.
