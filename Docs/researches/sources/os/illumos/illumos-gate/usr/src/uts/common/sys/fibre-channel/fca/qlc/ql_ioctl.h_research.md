# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/qlc/ql_ioctl.h

## Role

`ql_ioctl.h` declares the public internal entry points implemented by `ql_ioctl.c` for the `qlc` Fibre Channel adapter driver. It is a small prototype header with no data structure definitions.

## Interfaces

The file declares:
- Character-device entry points: `ql_ioctl`, `ql_open`, and `ql_close`.
- NVRAM utility load/dump helpers.
- VPD load/dump and VPD lookup helpers.
- Flash read/modify/write access through `ql_r_m_w_flash`.
- NVRAM read access through `ql_get_nvram`.

## Integration Notes

The header depends on illumos DDI types such as `dev_t`, `cred_t`, `intptr_t`, and `caddr_t`, plus `ql_adapter_state_t` from the `qlc` driver. It sits between the driver’s device-node control plane and lower flash/NVRAM/VPD management routines.
