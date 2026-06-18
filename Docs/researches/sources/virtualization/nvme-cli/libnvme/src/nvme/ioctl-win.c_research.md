# File Research: sources/virtualization/nvme-cli/libnvme/src/nvme/ioctl-win.c

Windows implementation of libnvme ioctl-style passthrough APIs. Unlike Linux, Windows does not expose one generic NVMe ioctl interface for all commands, so this file translates selected NVMe admin and I/O opcodes into Windows storage APIs.

Key behavior:
- Converts Windows `GetLastError()` and `STORAGE_PROTOCOL_STATUS_*` values into errno-style negative returns.
- Implements unsupported reset operations as `-ENOTSUP`; namespace rescan/block-size update use `IOCTL_DISK_UPDATE_PROPERTIES`.
- Derives namespace ID from `IOCTL_SCSI_GET_ADDRESS` by mapping SCSI LUN to `nsid = Lun + 1`.
- Provides generic `IOCTL_STORAGE_PROTOCOL_COMMAND` submission for vendor-specific commands and some WinPE-only cases.
- Maps NVMe flush/read/write to SCSI pass-through commands:
  - Flush -> `SCSIOP_SYNCHRONIZE_CACHE`
  - Read -> `SCSIOP_READ16`
  - Write -> `SCSIOP_WRITE16`
- Translates selected admin commands to Windows-specific mechanisms:
  - Get Log Page and Identify -> `IOCTL_STORAGE_QUERY_PROPERTY`
  - Set/Get Features -> storage protocol property set/query
  - Firmware Commit/Download -> `IOCTL_STORAGE_FIRMWARE_ACTIVATE` / `IOCTL_STORAGE_FIRMWARE_DOWNLOAD`
  - Format NVM -> WinPE passthrough or Windows sanitize/reinitialize IOCTL mapping
  - Security Send/Receive -> SCSI Security Protocol In/Out
- Dispatches public `libnvme_submit_io_passthru()` and `libnvme_submit_admin_passthru()` by opcode.

Important dependencies:
- Windows headers: `windows.h`, `winioctl.h`, `ntddscsi.h`.
- libnvme command opcode and bitfield helpers from `libnvme.h`, `types.h`, and `ioctl.h`.
- Transport hooks from `struct libnvme_transport_handle`: `submit_entry`, `submit_exit`, `decide_retry`, and global `dry_run`.

Research notes:
- The file preserves libnvme’s hook/retry semantics around every supported Windows submission path.
- Windows support is intentionally partial and command-specific; unsupported commands return `-ENOTSUP`.
- WinPE is detected through `HKLM\SYSTEM\CurrentControlSet\Control\MiniNT` and enables a few paths that normal Windows blocks.
- Result handling is often reduced to CQE DW0 or zero because Windows APIs do not expose full Linux-style NVMe completion details for every translated command.
