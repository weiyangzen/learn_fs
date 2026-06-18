# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_seek.c

## Purpose

`smb_seek.c` implements the legacy SMB seek command, which sets and returns the current file pointer associated with a FID. It exists for old clients; modern SMB reads and writes carry explicit offsets.

## Main Interfaces

- `smb_pre_seek()` starts DTrace accounting.
- `smb_post_seek()` finishes DTrace accounting.
- `smb_com_seek()` decodes and executes the seek.

## Behavior And Data Flow

`smB_com_seek()` decodes FID, seek mode, and signed 32-bit offset. It validates the FID, gets the ofile credential, delegates offset calculation and state update to `smb_ofile_seek()`, maps `EINVAL` to `ERRbadfunc` and other errors to server error, then encodes the resulting 32-bit offset.

Supported modes are start-of-file, current position, and end-of-file. Attempts to seek before the file start clamp to start via lower-level seek behavior. The file comment notes that offsets beyond 32-bit range are treated as errors rather than returning truncated low bits.

## Dependencies

This file depends on FID lookup, ofile credentials, `smb_ofile_seek()`, SMB result encoding, SMB error reporting, and DTrace probes.

## Notable Invariants And Risks

- The wire protocol exposes only 32-bit offsets, so this command is inappropriate for large-file positioning.
- Seek state is advisory and can be overwritten by subsequent read/write/seek requests.
- Correct large-offset rejection depends on `smb_ofile_seek()`.
