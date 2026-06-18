# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_print.c

## Purpose

`smb_print.c` implements legacy SMB print-share commands. It creates print spool files on printer shares, tracks spool documents for userland print handling, queues closed FIDs for printing, provides a minimal print queue response, and appends print data.

## Main Interfaces

- `smb_pre_open_print_file()`, `smb_post_open_print_file()`, and `smb_com_open_print_file()` handle `SMB_COM_OPEN_PRINT_FILE`.
- `smb_pre_close_print_file()`, `smb_post_close_print_file()`, and `smb_com_close_print_file()` close and queue spool files.
- `smb_pre_get_print_queue()`, `smb_post_get_print_queue()`, and `smb_com_get_print_queue()` return a minimal optional queue response.
- `smb_pre_write_print_file()`, `smb_post_write_print_file()`, and `smb_com_write_print_file()` append data to a spool file.

## Behavior And Data Flow

Open-print preprocessing decodes setup length, mode, and identifier string, synthesizes a unique path from the identifier plus an atomic temporary id, and configures the open as `FILE_OVERWRITE_IF` and `FILE_NON_DIRECTORY_FILE`. The command path requires print support enabled and a printer tree, calls `smb_common_create()`, returns the FID, then creates an `smb_kspooldoc_t` with physical spool path, client IP, username, FID, and a spool number assigned by `smb_spool_add_doc()`.

Close-print decodes a FID, verifies printer tree type, delegates actual close to `smb_com_close()`, and calls `smb_spool_add_fid()` so the server spooldoc ioctl path can wake userland spool monitoring.

Write-print allocates an `smb_rw_param_t`, decodes the FID, verifies print support and handle validity, gets current file size, decodes data into a VDB, sets the write offset to append at EOF, and delegates to `smb_common_write()`.

## Dependencies

This file depends on open/create/write/close common SMB handlers, share lookup for `SMB_SHARE_PRINT`, server spool helpers in `smb_server.c`, request-specific memory, DTrace SMB probes, and printer-share configuration in `sv_cfg.skc_print_enable`.

## Notable Invariants And Risks

- Print commands are rejected unless print support is enabled and the tree is `STYPE_PRN`.
- Spool document ownership uses the SMB user name from `sr->uid_user`.
- `smb_com_close_print_file()` still closes the FID if printing becomes disabled while the FID is open.
- Queue enumeration is intentionally minimal and optional.
- The generated spool path uses client-provided identifier text plus an atomic id; correctness depends on upstream path sanitization and normal create semantics.
