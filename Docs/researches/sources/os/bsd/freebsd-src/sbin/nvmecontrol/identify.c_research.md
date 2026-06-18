# File Research: sources/os/bsd/freebsd-src/sbin/nvmecontrol/identify.c

Implements `nvmecontrol identify` command and namespace identify printing.

Key behaviors:
- Supports hex output, verbose full-table hex output, and explicit NSID override.
- Resolves namespace device to controller device before issuing admin identify commands.
- Prints controller identify data through `nvme_print_controller()` from `identify_ext.c`.
- Prints namespace data including size/capacity/utilization, thin provisioning, LBA formats, metadata capabilities, data protection, multipath/reservation capabilities, deallocate behavior, optimal I/O fields, NVM capacity, NGUID, EUI64, and per-format details.
- In non-verbose hex mode truncates output before reserved trailing fields.

Research notes:
- This file owns namespace human-readable formatting; controller formatting is separated into `identify_ext.c`.
