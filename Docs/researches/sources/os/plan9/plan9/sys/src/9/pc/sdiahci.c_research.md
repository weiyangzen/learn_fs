# File Research: sources/os/plan9/plan9/sys/src/9/pc/sdiahci.c

Purpose: Plan 9 `SDifc` driver named `iahci` for AHCI SATA controllers. It handles PCI discovery, AHCI HBA setup, SATA drive state management, read/write DMA commands, ATAPI packet commands, SMART, cache flush, hotplug/media-change detection, and reset/recovery.

Main structures:
- `Ctlr`: AHCI controller state, PCI device, mapped HBA registers, raw/active drive arrays, enabled flag, interrupt counters.
- `Drive`: per-port state, associated `SDunit`, AHCI port and memory structures, disk state, negotiated SATA mode, identity data, serial/model/firmware strings, media-change flag, interrupt-jabber tracking.
- `Aportc`/`Aportm` from `ahci.h`: command-list, FIS, command-table, and per-port runtime state used by this file.

Key logic:
- `iapnp` scans PCI for Intel/ATI/Marvell/generic AHCI-like controllers, maps MMIO BAR, optionally forces Intel AHCI mode, configures HBA, and creates `SDev`s.
- `newctlr` maps implemented HBA ports into Plan 9 units, idles ports, and calls `configdrive`.
- `ahciconfigdrive`, `ahciidle`, `ahciquiet`, `ahcicomreset`, `ahciswreset`, and `ahciportreset` implement port initialization and reset paths.
- `satakproc` periodically runs `checkdrive` for all known drives, driving the state machine from missing/new/reset/error/offline to ready.
- `iainterrupt` reads HBA interrupt status, calls `updatedrive` for each active port, acknowledges interrupts, and detects interrupt storms.
- `iario` builds and submits AHCI read/write FIS commands for non-ATAPI disks. It handles SCSI flush commands and uses `sdfakescsi` for non-I/O SCSI emulation.
- `iariopkt` builds ATAPI packet commands for packet devices, including mode-sense handling through `sdmodesense`.
- `iarctl` and `iawctl` expose per-drive diagnostics/control: model/serial/firmware, SMART status, flags, registers, geometry, `change`, `flushcache`, `identify`, `mode`, `nop`, `reset`, `smart`, `smartenable`, `smartdisable`, and forced state.
- `iartopctl` reports controller-wide AHCI capability bits and port maps.

Dependencies and integration:
- Uses Plan 9 SD layer through `SDifc sdiahciifc`.
- Depends on `ahci.h`, PCI helpers, interrupt registration, `sdfakescsi`, `sdsetsense`, `sdmodesense`, and generic EHCI-style register memory coherence primitives.
- Uses a background kernel process for hotplug/spin-up polling.

Risks and notes:
- Uses only command slot 0 and caps normal disk I/O chunks to 128 sectors; it is simple rather than NCQ-oriented.
- Several reset and wait paths are timeout based and interact with a polling state machine; transient SATA link states can surface as retries or offline transitions.
- `resetdisk` marks `Ferror` under a condition that is logically always true (`state != Dready || state != Dnew`), likely intentional broad wakeup behavior but suspicious.
- Contains controller-specific Intel setup and generic fallback matching; unsupported AHCI variants may need quirks.
