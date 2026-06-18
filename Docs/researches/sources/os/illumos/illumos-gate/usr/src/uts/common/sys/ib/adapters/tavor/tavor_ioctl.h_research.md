# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/adapters/tavor/tavor_ioctl.h

## Role

`tavor_ioctl.h` defines the ioctl interface for Tavor driver control, diagnostics, firmware flashing, flash access, VTS status, loopback testing, and DDR reads.

## Major Definitions

The header declares `tavor_ioctl()` and defines the ioctl command base. In debug builds it includes register read/write ioctl commands; non-debug builds expose flash read/write/erase/init/fini, loopback, info, ports, and DDR read commands.

Flash constants define read/write/erase operation types, default sector/device sizes, CFI init command, legacy and expanded CFI data sizes, and supported flash command-set IDs for Intel, AMD, and unknown command sets.

The ioctl data structures include:
- `tavor_fw_info_ioctl_t` for firmware version.
- `tavor_flash_ioctl_t` for sector, quadlet, byte, and erase operations.
- `tavor_flash_init_ioctl_t` for hardware revision, firmware revision, CFI info, and part number.
- `tavor_reg_ioctl_t` for debug register access.
- `tavor_stat_port_ioctl_t` and `tavor_ports_ioctl_t` for VTS port state.
- `tavor_ddr_read_ioctl_t` for aligned 32-bit DDR reads.
- `tavor_loopback_error_t` for loopback failure classification.
- `tavor_loopback_ioctl_t` for loopback buffers, iteration/retry/timeout settings, pass count, failure buffer, and error type.
- `tavor_info_ioctl_t` for firmware/hardware version, flash size, and accessible DDR range.

## Interfaces

Only `tavor_ioctl()` is declared here. Helpers and 32-bit compatibility forms live in other headers/source files.

## Integration Notes

This header is a user-kernel ABI surface. Structure layout and revision fields matter for tools such as VTS and firmware-update utilities. Some interfaces are gated by `DEBUG`.
