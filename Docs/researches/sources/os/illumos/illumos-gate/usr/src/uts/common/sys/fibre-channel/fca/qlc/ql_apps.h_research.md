# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/qlc/ql_apps.h

This header defines QLogic application/utility-facing structures and ioctl command constants used by tools such as `qladm` and `qlctest`.

Key contents:
- Firmware trace buffer sizes `FWEXTSIZE` and `FWFCESIZE`.
- ISP8100 extended initialization control block `ql_ext_icb_8100_t`, including FCF matching, VLAN ID, fabric name, and proposed MAC address.
- Adapter revision-level structure `ql_adapter_revlvl_t`.
- Application mailbox command structure `app_mbx_cmd_t`.
- Diagnostic loopback parameter structure `lbp_t`, with different pointer widths under `apps_64bit`.
- Diagnostic operation IDs for command queue check, firmware checksum, self-test, revision level, mailbox/data loopback, firmware execution, adapter feature bits, NVRAM defaults, and ECHO.
- Utility ioctl command values for load/dump, FOAPI reserved range, and admin operations.
- Admin command enum `ql_adm_cmd_t` for extended logging, adapter info, device list, loop reset, firmware dump/trigger, beacon, NVRAM, flash, property updates, VPD, and firmware module update.
- Admin operation envelope `ql_adm_op_t`.
- Adapter info payload `ql_adapter_info_t`.
- Port-type enum and device-info payload for admin device listing.

Dependencies:
- Includes `sys/scsi/scsi_types.h`.
- Shares types with `ql_api.h` and `ql_init.h`.

Research notes:
- This file is a smaller, utility-facing ABI separate from the broader SAN/device-management ABI in `exioct.h`.
- The `apps_64bit` conditional in `lbp_t` is a direct user/kernel compatibility concern for diagnostic loopback buffers.
