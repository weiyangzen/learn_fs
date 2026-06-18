# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_flush.c

## Role

Implements SMB1 Flush, synchronously pushing cached file data and allocation information to stable storage.

## Major Responsibilities

- Decodes the target FID.
- Short-circuits when global flush enforcement is disabled.
- Flushes one open file when the FID is valid.
- Flushes all open files on the tree when FID is `0xFFFF`.
- Protects the tree open-file list while iterating.
- Encodes an empty SMB success response.

## Key Functions

- `smb_pre_flush()` decodes `sr->smb_fid` and emits DTrace start.
- `smb_post_flush()` emits DTrace done.
- `smb_com_flush()` validates the FID or iterates the tree open-file list and calls `smb_ofile_flush()`.

## Research Notes

The all-files path enters the tree open-file AVL as a reader and locks each `smb_ofile_t` around flushing because the flush may block.
