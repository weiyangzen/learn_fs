# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/ufs_prot.h

## Role

Generated RPC protocol header for the UFS daemon (`ufsd`) repair, event, and log-message interface.

## Key Protocol Types

- `ufsdrc_t` maps protocol results to errno-like values plus `UFSDRC_EXECERR` and `UFSDRC_ERR`.
- `fs_identity_t` identifies a filesystem by 32-bit device and name.
- `ufsd_repairfs_args_t` and `ufsd_repairfs_list_t` describe repair requests and batches.
- Event enums cover reboot, fsck, and log operations.
- Boot, log operation, and fsck state enums model daemon event payloads.
- `ufsd_log_data_t`, `ufsd_log_msg_t`, `ufsd_msg_vardata_t`, and `ufsd_msg_t` encode variable event/log messages.

## RPC Interface

Defines service name `ufsd`, version constants, RPC program `100233`, procedures:
- `UFSD_NULL`
- `UFSD_REPAIRFS`
- `UFSD_REPAIRFSLIST`
- `UFSD_SEND`
- `UFSD_RECV`
- `UFSD_EXIT`

Also declares client/server stubs, free-result function, and XDR routines for each protocol type.

## Risk Notes

The header says it is rpcgen-generated and should not be manually edited. Kernel XDR code depends on `UFSD_THISVERS`; protocol changes require corresponding XDR updates.
