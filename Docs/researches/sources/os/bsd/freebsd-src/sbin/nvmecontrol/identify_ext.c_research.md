# File Research: sources/os/bsd/freebsd-src/sbin/nvmecontrol/identify_ext.c

Provides `nvme_print_controller()`, the human-readable controller identify formatter shared by identify and discovery verbose output.

Key behaviors:
- Prints controller identity, serial/model/firmware strings, OUI, multipath capabilities, transfer limits, sanitize capabilities, controller type, keep-alive, max commands, and version.
- Prints admin command set attributes, firmware slots, error log entries, power states, NVM capacity, firmware update granularity, and host memory buffer sizes.
- Prints NVM command set attributes such as queue entry sizes, namespace count, supported I/O commands, fused operations, format attributes, volatile write cache, and NVM subsystem name.
- Prints fabrics attributes when present: capsule sizes, in-capsule data offset, controller model, max SGL descriptors, and disconnect support.

Research notes:
- This is display-only but depends heavily on NVMe bitfield macros for correct decoding.
