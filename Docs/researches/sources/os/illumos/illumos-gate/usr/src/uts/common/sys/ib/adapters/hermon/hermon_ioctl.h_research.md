# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/adapters/hermon/hermon_ioctl.h

## Purpose
Defines the Hermon ioctl interface for firmware/flash operations, VTS diagnostics, register access in debug builds, port reporting, loopback testing, and adapter information.

## Main Interfaces
- `hermon_ioctl()` driver entry point prototype.
- Ioctl command base `HERMON_IOCTL` uses the Tavor-compatible `'t' << 8` value for VTS consistency.
- Commands include flash read/write/erase/init/fini, loopback, info, ports, DDR read, boot address write, and debug-only register read/write.
- Flash operation constants for sector/quadlet read, sector/byte write, sector/chip erase.
- Flash defaults and CFI sizing constants, including AMD, Intel, SPI, and unknown command-set identifiers.
- Public ioctl structs:
  - `hermon_fw_info_ioctl_t`
  - `hermon_flash_ioctl_t`
  - `hermon_flash_init_ioctl_t`
  - `hermon_reg_ioctl_t`
  - `hermon_stat_port_ioctl_t`
  - `hermon_ports_ioctl_t`
  - `hermon_loopback_ioctl_t`
  - `hermon_info_ioctl_t`
- `hermon_loopback_error_t`: detailed failure enum for VTS loopback setup, QP transitions, WQE post, CQ poll, and data comparison.

## Dependencies And Relationships
Includes `sys/cred.h`. 32-bit compatibility wrappers and loopback internal state are defined in `hermon_misc.h`. Flash register constants are in `hermon_hw.h`.

## Research Notes
The externally visible structures contain user pointers (`caddr_t`) and revision fields, so ioctl implementations must handle copyin/copyout, model conversion, and version validation carefully.
