# File Research: sources/os/bsd/freebsd-src/sbin/nvmecontrol/modules/samsung/samsung.c

Vendor-specific Samsung extended SMART log formatter.

Key behaviors:
- Defines packed `struct samsung_log_extended_smart`.
- Decodes the initial SMART key/value region, including program/erase fail counts, wear leveling, end-to-end errors, CRC errors, media wear, host read percentage, workload timer, thermal throttle, and lifetime write counters.
- Prints Samsung-specific extended fields including write amplification, lifetime user/NAND writes, lifetime reads, retired block count, current temperature, capacitor health, reserved erase blocks, read reclaim count, uncorrectable ECC count, reallocated blocks, power-on hours, power-off counts, and performance indicator.
- Registers page `0xca` under vendor `"samsung"`.

Research notes:
- Combines generic 12-byte SMART records with a larger Samsung-specific packed tail.
