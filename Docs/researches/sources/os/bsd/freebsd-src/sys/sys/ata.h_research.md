# File Research: sources/os/bsd/freebsd-src/sys/sys/ata.h

ATA/ATAPI protocol, identify data, log, and ioctl definitions.

Key elements:
- Defines packed `struct ata_params`, mapping ATA IDENTIFY DEVICE words and many capability/status bits.
- Defines dataset management, device/status/error register bits, HPA feature codes, transfer modes, ATA commands, NCQ commands, ZAC zone-management commands, security commands, and ATAPI command opcodes.
- Defines ATA channel/device ioctl structures and ioctl codes.
- Defines packed `struct atapi_sense`.
- Defines Extended Power Conditions constants and power condition log structures.
- Defines ATA general-purpose log directory, identify log page, capacity page, supported capabilities page, and zoned device information page structures.
- Defines `struct ata_ioc_request`, `struct ata_security_password`, and ATA RAID config/status ioctl structures and command codes.

Dependencies:
- Includes `sys/types.h` and `sys/ioccom.h`.

Research notes:
- Core storage protocol ABI header for ATA disks, ATAPI devices, and legacy ATA RAID management.
- Highly relevant to block storage and filesystem layers because it exposes capacity, sector size, trim support, write cache, flush, FUA, NCQ, sanitize, security, power, and zoned-device capabilities.
