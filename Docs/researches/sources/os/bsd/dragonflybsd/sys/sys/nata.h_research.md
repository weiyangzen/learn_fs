# File Research: sources/os/bsd/dragonflybsd/sys/sys/nata.h

ATA/ATAPI parameter, command, sense, ioctl, and RAID control ABI.

Key responsibilities:
- Defines packed `struct ata_params`, matching the ATA IDENTIFY DEVICE word layout through word 255.
- Defines ATA protocol, ATAPI type, DRQ, capability, validity, SATA, command support/enabled, UDMA, cable, acoustic, queue, and size-related bit constants.
- Defines ATA transfer mode constants for PIO, WDMA, UDMA, SATA, and USB modes.
- Defines ATA and ATAPI command opcodes and subfeature constants.
- Defines channel/device ioctl structures and ioctls.
- Defines packed ATAPI request sense structure and sense-key constants.
- Defines `struct ata_ioc_request` for raw ATA/ATAPI requests.
- Defines device ioctls for raw request, parameter retrieval, mode get/set, and spindown get/set.
- Defines ATA RAID config/status structures, RAID type/status/disk flags, and RAID management ioctls.

Important behavior:
- The identify structure is packed and laid out by ATA word numbers; comments annotate word offsets.
- Raw requests support both ATA register-style command fields and ATAPI CCB/sense data.
- RAID ioctl structures use fixed arrays of 16 disks.

Dependencies:
- Includes `sys/types.h` and `sys/ioccom.h`.

Notable risks:
- `struct ata_params` is hardware/ABI layout; alignment or packing changes would break parsing.
- Userland raw ATA ioctls pass data pointers and command flags, so kernel validation is critical.
- Several sense bit macros include trailing semicolons in their definitions, which can surprise expression-style macro use.
