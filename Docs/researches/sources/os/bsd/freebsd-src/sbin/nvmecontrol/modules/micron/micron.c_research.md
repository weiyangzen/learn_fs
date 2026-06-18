# File Research: sources/os/bsd/freebsd-src/sbin/nvmecontrol/modules/micron/micron.c

Vendor-specific Micron NVMe SMART log formatter.

Key behaviors:
- Decodes vendor unique SMART log page `0xca`.
- Handles NAND writes/reads in GiB, thermal throttle status, temperature max/min/current, power consumption, power-loss protection, and generic key/value counters.
- Registers vendor log page under vendor name `"micron"`.

Research notes:
- Uses 12-byte SMART key records and stops after 150 bytes, matching the Intel-style additional SMART layout.
