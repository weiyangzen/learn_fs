# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/qlge/qlge_hw.h

## Role

`qlge_hw.h` is the fixed hardware/register/firmware ABI header for the illumos `qlge` QLogic Ethernet driver. It defines bit constants, register offsets, mailbox structures, flash layouts, ioctl payloads, core-dump formats, queue initialization blocks, and network IOCB formats.

## Major Definitions

The file starts with general constants:
- Schultz adapter/device identification.
- Mailbox register counts.
- `BIT_0` through `BIT_31`.
- `ql_stats_t`, the driver-visible statistics bundle for interrupts, speed, duplex, TX/RX counters, multicast/broadcast counters, CRC/errors, and hardware stats.
- Ethernet CRC size and processor/mailbox address register constants.

Hardware register sections define bit fields for:
- System, reset/failover, function-specific control, host command/status, configuration, status, revision ID, forced ECC error, error status, semaphores, completion queue stop, MAC address index, split-header, NIC receive config, routing index, CAM output routing, completion queue interrupt status, processor address, host command, XGMAC access, MAC protocol address control, TX/RX config, pause frames, and XGMAC statistics.

Networking and queue definitions include:
- Interrupt enable/disable macros.
- Completion queue, RX ring, and TX ring limits.
- Large-buffer queue and buffer queue address elements.
- Link state enum.
- Work queue initialization block `wqicb_t`.
- Completion queue initialization block `cqicb_t`.
- RSS initialization block `ricb`.
- Host command IOCB opcodes.
- OAL entries and outbound MAC request/response IOCBs.
- Inbound MAC response IOCB with checksum, VLAN, RSS, split-header, buffer-selection, and receive error flags.
- System event IOCB with link, CAM, ECC, management fatal, MAC interrupt, and PCI buffer-read error events.
- Generic network response IOCB and request/response entry-size macros.

Control-plane and diagnostic definitions include:
- ioctl command base `QLA_IOC` and commands for PCI/register access, debug level get/set, flash read/write, VPD read, properties, adapter listing, firmware image read/write, staged copy in/out, core dump, system error trigger, and soft reset.
- ioctl payload structures for header metadata, PCI/device registers, flash I/O, MPI version, link status, adapter properties, adapter info, dump headers/image headers/footer, and crash records.
- Mailbox timeout, IDC destination function enums, firmware/PHY version structures, port config structures, mailbox command/data structures, and NIC mailbox register locations.
- MPI core dump global/segment headers and segment numbering for mailbox/control/XGMAC/MAC protocol regions.

Flash and firmware layout support includes:
- Flash register flags and SPI commands.
- Flash chip info and flash description table.
- Manufacturer/device IDs and flash type flags.
- PCI option ROM header/data structures.
- Flash layout table data structure (`QFLT`) and image layout table (`QFIM`) structures.
- Image entry, timestamp, description header, flash layout table header/entry/container, and NIC configuration table with factory/CLP MAC and VLAN data.

## Endianness and ABI Notes

The file provides conditional endian-conversion macros for little-endian and big-endian builds, backed by `ql_change_endian`. It also uses packed hardware structures and restores packing after IOCB definitions. The structure layouts are consumed directly by firmware, DMA rings, ioctl clients, and flash parsers, so sizes and field ordering are part of the hardware/driver ABI.

## Integration Notes

`qlge_hw.h` is included by `qlge.h` and provides most of the constants referenced by initialization, interrupt, flash, MPI, ioctl, TX/RX, and GLD code. It intentionally mixes register maps, firmware mailbox data, ioctl payloads, and flash metadata because those surfaces all describe the same adapter hardware contract.
