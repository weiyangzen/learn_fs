# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/adapters/scsi_vhci.h

## Purpose
Global include for illumos SCSI virtual HCI multipathing. It defines kernel-private packet/LUN/path/HBA state, failover module interfaces, persistent reservation helpers, path operation descriptors, ioctl ABI structures, and multipath ioctl command numbers.

## Main Interfaces
- Kernel macros map transports, packets, SCSI addresses, VHCI packets, and path-private structures; hold/release LUNs during failover/reservation-sensitive operations; and count outstanding path commands.
- `vhci_pkt` links target-driver packets to physical HBA packets and records binding path, init-packet arguments, retry/original packet state, and VHCI packet flags.
- `scsi_vhci_lun_t` tracks per-virtual-LUN locks, transient/failover state, active pathclass, failover ops, reservation/PGR state, path update state, LUN reset support, sector size, and failover support mode.
- `scsi_vhci_priv_t` is pathinfo client-private state with per-path command count, associated physical `scsi_device`, external failover watch token, and new-path cleanup marker.
- `scsi_vhci_t` is VHCI soft state with device info, HBA transport, taskqs, reset notification list, config flags, and MPAPI private state.
- `scsi_failover_ops` defines the pluggable failover module ABI: probe/unprobe, activate/deactivate, get opinfo, ping, sense analysis, and pathclass iteration.
- Userland structs and constants define path property buffers, path info, ioctl arguments, controller switching, and `SCSI_VHCI_*` ioctl subcommands.

## Dependencies And Relationships
Includes task queues, multi-host disk support, MDI/MPAPI headers, and SCSI adapter MPAPI definitions. Used by the scsi_vhci driver and failover modules such as TPGS and symmetric failover providers.

## Research Notes
The header has both kernel and userland sections. The failover contract is modular, while the ioctl ABI exposes client/PHCI path queries and administrative path state changes.
