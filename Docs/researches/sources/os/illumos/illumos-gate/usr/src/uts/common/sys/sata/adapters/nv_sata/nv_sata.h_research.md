# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sata/adapters/nv_sata/nv_sata.h

## Role

Private header for the illumos NVIDIA SATA HBA driver. It defines the controller, port, command slot, DMA PRD, interrupt, reset, NCQ, hotplug, and optional SGPIO state used by the `nv_sata` adapter.

## Key Elements

- `nv_ctl_t` holds controller-wide state: BAR handles/addresses, PCI identity, interrupt handles, SATA HBA transport, chipset-specific interrupt/register hooks, MCP5x/CK804 register pointers, controller lock, DMA capability flags, and SGPIO common state when enabled.
- `nv_port_t` holds per-port state: task-file register pointers, bus-master registers, SATA SCRs, slot array, NCQ counters, reset/link-event timing, hotplug/reset flags, condition variables, and debug counters.
- `nv_slot_t` binds an active SATA packet to data-buffer state, request-sense buffer, start/intr callbacks, and slot flags.
- `nv_sgp_cmn` and `nv_sgp_cbp2cmn` coordinate SGPIO LED taskq/common data across controllers when `SGPIO_SUPPORT` is enabled.
- Defines chipset register offsets and bits for task-file I/O, bus-master DMA, MCP5x NCQ/interrupt registers, CK804 interrupt status, ADMA reset/hotplug controls, and SATA SCR offsets.
- Defines ATA reset signatures for disk, ATAPI, port multiplier, and no-device cases.
- Defines timing constants for resets, signature polling, link-event settling, interrupt loop limits, and debug throttling.
- Defines attachment progress flags and port/controller state flags used for teardown and recovery.

## Dependencies and Coupling

This header is tightly coupled to illumos DDI/DKI types, `sata_hba_t`/`sata_pkt_t`, PCI BAR layout, chipset-specific register maps, and optional SGPIO support from `nv_sgpio.h`.

## Research Notes

The file is driver-private infrastructure rather than a public ABI. Most constants encode hardware behavior and timing assumptions. The NCQ model is conservative: the per-port state tracks NCQ and non-NCQ exclusivity, active slots, queue depth, and cached SActive state to serialize command modes safely.
