# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/qlc/ql_init.h

This header defines QLogic adapter initialization, NVRAM, firmware dump, dump-template, NVRAM access, device-list, and initialization lifecycle interfaces.

Key contents:
- External task callback delay `ql_task_cb_dly`.
- Classic ISP2200-style `nvram_t` layout, including firmware options, frame/IOCB/execution settings, WWPN/WWNN, connection options, host parameters, boot target data, adapter features, subsystem IDs, and checksum.
- 24xx+ `nvram_24xx_t` layout with initialization control data, firmware options, serial link controls for multiple adapter families, FCoE/MAC fields, host/BIOS/boot parameters, CLP flags, default names, enhanced features, firmware table pointers, model fields, feature masks, subsystem IDs, and checksum.
- Firmware dump sizes for 2200, 2300, 6322, 24xx, 25xx, 81xx, 27xx, and 83xx adapters.
- VPD and SFP sizes.
- Firmware dump structures:
  - `ql_fw_dump_t` for 2200/2300-era devices.
  - `ql_24xx_fw_dump_t`
  - `ql_25xx_fw_dump_t`
  - `ql_81xx_fw_dump_t`
  - `ql_83xx_fw_dump_t`
- Kernel-only dump-template entry type constants and structures for template headers, entry headers, I/O register reads/writes, PCI reads/writes, RAM reads, queue/FCE capture, RISC pause/resume, interrupt disable, host-buffer dumps, scratch capture, register reads/writes, and raw dump data.
- NVRAM lock flags for NVRAM and VPD data.
- Product ID constants after reset.
- NVRAM command bit definitions for start, read, write, erase, mask, and delay.
- Device ID list structures for old, extended, and 24xx formats, plus union `ql_dev_id_list_t`.
- Device-list entry count `DEVICE_LIST_ENTRIES`.
- Kernel prototypes for adapter initialization, PCI/SBus config, NVRAM config/read/write/lock/release, property handling, firmware load/start, cache-line setup, ring init, firmware readiness, device-list parsing, chip reset, ISP abort, command requeue, and virtual-port control/create/destroy.

Dependencies:
- Uses constants/types from `ql_api.h` and `ql_apps.h`, including queue sizes, `ql_ext_icb_8100_t`, and `ql_adapter_state_t`.
- Kernel-only section depends on many `BIT_*` constants and qlc core types.

Research notes:
- This file is adapter-generation compatibility-heavy. NVRAM and dump layouts are hardware/firmware contracts and should not be casually refactored.
- Firmware dump structures include variable/extensible tails for trace buffers and extended memory.
- The kernel-only dump-template structures describe a firmware-provided or module-provided recipe for capturing hardware state.
