# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sata/adapters/ahci/ahcivar.h

## Role

`ahcivar.h` defines private AHCI driver state: address qualifiers, port-multiplier information, per-port DMA/command/event state, controller state, capability flags, attach-state tracking, debug controls, timing constants, and enclosure-management message layouts.

## Addressing

`ahci_addr_t` identifies an HBA port and optional port-multiplier port with qualifier bits for null, port, PM port, and port multiplier. Macros test validity and initialize direct port, PM port, or PMULT addresses.

## Port State

`ahci_pmult_info_t` stores port-multiplier device count, per-PM-port device types/states, NCQ PM port, and pending notification tags.

`ahci_port_t` tracks one HBA port:
- physical port number, device type, port state, PM info.
- flags for mopping, polling, request sense, started, read-log-ext, no-device, port-multiplier read/write, ignored IPMS, PMULT notification, hotplug, and error printing.
- received-FIS DMA state.
- command-list and command-table DMA/access handles.
- sync command condition variable and port mutex.
- NCQ limits, pending non-NCQ/NCQ tags, slot packets/timeouts.
- completed packet queue.
- PRD byte counts.
- error-retrieval and PMULT read/write packets.
- reset-in-progress flag.
- event taskq/args and mop counter.

Warlock annotations document mutex protection.

## Controller State

`ahci_ctl_t` records devinfo, PCI IDs, port/cport mappings, port counts, implemented-port bitmap, port pointers, flags, power state, PCI config handle, AHCI BAR mapping, SATA framework transport, DMA attributes, watchdog timeout, mutex, interrupt handles/metadata, FMA capability, and enclosure-management state.

Controller flags cover attach, detach, suspend, and quiesce. Capability bits include PIO multiple DRQ, command-list limitations, NCQ, power management, 32-bit DMA constraints, SCLO, initialization reset, SNotification, port multiplier switching modes, SRST quirk, enclosure services, and DevSleep.

## Support Macros

The header provides helpers for command-in-progress classification, command type constants, attach-state milestones, delay/poll constants, bit set/clear, debug categories, and `AHCIDBG()` tracing/logging.

Enclosure-management definitions include buffer sizing, LED message values, message types, and packed LED/header message structures.

## Research Notes

This is the AHCI driver’s central private state header. The major invariants are per-port mutex protection, command-slot tag accounting, NCQ versus non-NCQ exclusion, port-multiplier state routing, attach unwind state bits, and enclosure-management readiness flags.
