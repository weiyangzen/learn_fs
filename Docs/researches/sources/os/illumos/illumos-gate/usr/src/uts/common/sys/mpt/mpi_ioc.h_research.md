# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/mpt/mpi_ioc.h

MPT MPI IOC management, discovery event, and firmware image ABI header.

Key responsibilities:
- Defines IOC init request/reply frames, WhoInit values, init flags, message/header version masks, reply frame sizing, high address fields, and host page buffer SGE.
- Defines IOC facts and port facts request/reply structures with firmware version, product ID, queue depths, chain depth, ports, devices/buses, capabilities, exceptions, and protocol flags.
- Defines port enable, event notification, and event acknowledge messages.
- Defines event IDs and event payloads for IOC state, SCSI/SAS device status changes, queue full, FC link/loop/logout, integrated RAID changes, SAS PHY link status, discovery errors, expander status changes, persistent table full, and log entries.
- Defines firmware download/upload messages, transaction context SGEs, firmware image headers, product/family ID masks, and extended image headers.

Dependencies:
- Uses SGE unions and common IOC status constants from `mpi.h`.
- Event payloads overlap semantically with RAID/config/SAS page definitions in sibling MPT headers.

Notable risks:
- Event payloads are variable and keyed by event ID; consumers must validate event length before casting.
- Firmware image/header constants are update-path ABI and mistakes can brick or misidentify adapter images.
