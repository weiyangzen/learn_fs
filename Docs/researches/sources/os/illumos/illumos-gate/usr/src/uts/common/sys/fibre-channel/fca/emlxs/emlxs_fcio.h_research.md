# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/emlxs_fcio.h

Purpose: Defines Emulex-specific FCIO diagnostic ioctl command IDs, driver-specific error codes, parameter/VPD/PHY/throttle/log structures, and queue-stat reporting structures.

Key definitions:
- `FCIO_REV` is 2.
- Diagnostic ioctl namespace starts at `EMLXS_DIAG` and includes BIU/POST/ECHO diagnostics, parameter get/set/list, boot revision/download/state, CFL download, VPD, DFC command, DFC revision, PHY get, throttle get/set, and VPD v2.
- Special debug/test ioctls include BAR I/O, test code, hardware error test, and mailbox timeout test.
- Dump file IDs: TXT, DMP, CEE, FAT.
- Error codes range from `EMLXS_TEST_FAILED` through `EMLXS_REBOOT_REQUIRED`.
- `emlxs_parm_t`: user-visible driver parameter descriptor with label, min/max/default/current, flags, and help text.
- Parameter flags include dynamic, boolean, hex, dynamic reset-required, and dynamic link-reset-required.
- `emlxs_vpd_desc_t` and `_v2_t`: fixed-size VPD description formats; v2 expands fields to 256 bytes.
- `emlxs_phy_desc_t`, `emlxs_throttle_desc_t`, `emlxs_log_req_t`, `emlxs_log_resp_t`.
- FCIO queue descriptors model EQ/CQ/WQ/RQ host index, max index, queue IDs, linkage, physical/virtual addresses, interrupt vector, and statistics.
- `FCIO_Q_STAT_t`: aggregate queue statistics for all supported EQ/CQ/WQ/RQ objects plus timer and interrupt counts.

Dependencies and interactions:
- Used by ioctl/DFC paths and log retrieval declarations in `emlxs_extern.h`.
- Queue limits mirror SLI4 queue limits: 8 EQs, 4 WQs per EQ, 2 RQs, and CQs derived from WQ/RQ/MQ requirements.

Implementation notes:
- This header is a user/kernel ABI surface; structure sizes and command values are compatibility-sensitive.
- Virtual addresses are split into 32-bit `virt` and `virt_hi` fields for reporting.
