# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/netsmb/smb_subrs.c

## Scope

This file provides shared netsmb helpers for credential lifetime, debug/error reporting, SMB/NT status translation, on-the-wire string conversion, SMB1/SMB2 create/close dispatch, and common read/write UIO chunking.

## APIs And Behavior

- `smb_credinit()` and `smb_credrele()` wrap kernel credentials for SMB operations. On labeled systems, credentials are duplicated and marked `NET_MAC_AWARE`.
- `smb_errmsg()` backs SMB debug/error macros, sending debug events to DTrace and non-debug errors to `vcmn_err()`.
- `m_dumpm()` emits DTrace probes describing STREAMS mblk chains.
- Large static tables map NT status values to Unix errno and DOS error class/code values.
- `smb_maperr32()` maps NT status to errno, first through direct NT-to-errno mapping, then through NT-to-DOS and DOS-to-errno fallback.
- `smb_doserr2status()` maps DOS class/code pairs back to NT status.
- `smb_maperror()` maps classic SMB DOS/SRV/HRD error classes to errno, logging unknown values.
- `smb_get_dstring()` decodes SMB strings from wire form into UTF-8, using UTF-16LE conversion when Unicode negotiation is active.
- `smb_put_dmem()` and `smb_put_dstring()` encode SMB path/name data into mbchains, with UTF-8 to UTF-16LE conversion and Unicode alignment padding.
- `smb_smb_ntcreate()` and `smb_smb_close()` dispatch common file-handle operations to SMB2 or SMB1 implementations based on `SMBV_SMB2`.
- `smb_rwuio()` dispatches SMB1 readx/writex or SMB2 read/write and chunks transfers according to negotiated maximum I/O sizes.

## State And Dependencies

- Depends on `netsmb/smb_conn.h`, `smb_rq.h`, `smb_subr.h`, mchain helpers, NT status constants, SMB1/SMB2 request implementations, and illumos credential/DTrace facilities.
- `smb1_large_io_max` caps SMB1 large read/write requests at 60 KiB despite protocol maxima.

## Risks And Invariants

- NT/DOS error mapping is policy-sensitive; unmapped statuses collapse to `EIO`.
- String conversion assumes modern Unicode-capable servers; non-Unicode paths are copied as-is with comments noting missing OEM conversion.
- `smb_rwuio()` relies on lower-level I/O functions updating the `uio`; double-updating would corrupt offsets and residuals.
- On partial transfer followed by error, `smb_rwuio()` suppresses the error to preserve POSIX short-I/O semantics.
