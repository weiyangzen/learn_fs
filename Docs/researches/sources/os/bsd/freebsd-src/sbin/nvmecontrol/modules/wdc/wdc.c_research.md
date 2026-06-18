# File Research: sources/os/bsd/freebsd-src/sbin/nvmecontrol/modules/wdc/wdc.c

Purpose: Implements the dynamically registered `nvmecontrol wdc` vendor command group and WDC/HGST-specific log page decoders.

Key behavior:
- Registers `wdc` and subcommand `cap-diag`.
- Supports WDC vendor IDs `0x1c58`, `0x1b96`, and `0x15b7`.
- For older WDC devices, retrieves cap-diag data via vendor opcode `0xe6`; for newer SanDisk/WDC VID `0x15b7`, retrieves DUI/cap-diag data via opcode `0xfa`.
- Appends the controller serial number and suffix to the user-provided output path template before writing binary dumps.
- Uses `NVME_PASSTHROUGH_CMD` and `NVME_GET_MAX_XFER_SIZE` to chunk vendor log reads.
- Registers `hgst` and `wdc` log page handlers for `HGST_INFO_LOG`, printing detailed health/SMART subpages.

Important internals:
- `wdc_get_data()` and `wdc_get_data_dui()` build vendor passthrough commands with different offset dword placement.
- `wdc_get_dui_log_size()` decodes DUI headers for versions 0-3 and optionally limits collection by data area.
- HGST log printing uses a subtype dispatch table for write/read/verify errors, self-test, background scan, erase errors/counts, temperature history, SSD performance, and firmware load data.

Dependencies:
- `nvmecontrol.h` helpers: `read_controller_data()`, `kv_lookup()`, `NVME_LOGPAGE`.
- FreeBSD NVMe ioctl ABI: `struct nvme_pt_command`, `NVME_PASSTHROUGH_CMD`, `NVME_GET_MAX_XFER_SIZE`.
- Endian helpers from `<sys/endian.h>`.

Research notes:
- This file is both a command module and a log-page plugin.
- Error handling is fail-fast via `err()`/`errx()`.
- Output dump overwrite protection is explicitly marked as missing by an `XXX` comment.
