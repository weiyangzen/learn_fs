# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fctio.h

## Role

`fctio.h` defines the FC target ioctl ABI used to query target HBA/port information, statistics, link status, and force LIP.

## Ioctl Envelope And Commands

- Defines `FCT_IOCTL`, `FCTIO_CMD`, and `FCTIO_SUB_CMD`.
- Subcommands include adapter list, adapter attributes, adapter port attributes, discovered port attributes, port attributes, adapter port stats, link status, and force LIP.
- Defines transfer direction flags `FCTIO_XFER_NONE`, `FCTIO_XFER_READ`, `FCTIO_XFER_WRITE`, and `FCTIO_XFER_RW`.
- `fctio_t` is the ioctl envelope with transfer, command, flags, command flags, input/output/aux lengths, error code, and 64-bit user buffer addresses.

## HBA And Port Structures

- `fc_tgt_hba_list_t` is a variable-length list of port WWNs.
- `fc_tgt_hba_adapter_attributes_t` reports manufacturer, serial, model, model description, node WWN, node symbolic name, hardware/driver/option ROM/firmware versions, vendor id, number of ports, and driver name.
- `fc_tgt_hba_port_attributes_t` reports last change, node/port WWNs, FC id, type/state, supported class, supported/active FC-4 types, symbolic name, supported/current speed, max frame size, discovered-port count, and fabric name.
- `fc_tgt_hba_adapter_port_stats_t` reports reset age, Tx/Rx frames and words, LIP/NOS, error/dumped frames, and link/sync/signal/protocol/invalid word/CRC counts.

## Constants

Defines T11 FC-HBA port type, port state, and port speed constants, including 1/2/4/8/10/16/32 Gbit and not-negotiated. Defines ioctl result codes and sysevent class/subclass strings for sunfc port attach/detach/online/offline/RSCN and target add/remove.
