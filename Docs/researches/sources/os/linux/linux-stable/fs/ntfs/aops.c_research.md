# File Research: sources/os/linux/linux-stable/fs/ntfs/aops.c

## Summary
Implements NTFS address-space operations for page-cache read, readahead, writeback, block mapping, swap activation, and MFT-specific writeback integration.

## Main APIs
- `ntfs_read_folio()`.
- `ntfs_bmap()`.
- `ntfs_readahead()`.
- `ntfs_writepages()`.
- `ntfs_swap_activate()`.
- Address-space operation tables `ntfs_aops` and `ntfs_mft_aops`.

## Behavior
Reads use iomap bio reads with a custom end-io handler that zeros bytes beyond initialized size inside partially initialized folio ranges. Encrypted attributes are rejected because EFS is unsupported; compressed nonresident data is delegated to the NTFS compression reader. Readahead is skipped for resident and compressed files. Writeback uses iomap for nonresident attributes unless the volume is shutting down or the file is encrypted.

## State and Synchronization
`ntfs_bmap()` reads initialized size under `ni->size_lock`, then maps VCN to LCN under `ni->runlist.lock`. It returns zero for holes, sparse/uninitialized ranges, unsupported attribute types, and errors. Iomap operation tables are supplied by NTFS read/writeback code in neighboring files.

## Risks
`bmap()` cannot distinguish block zero from hole/error, which is called out for `$Boot`. Initialized-size handling is important to avoid exposing stale data. Encrypted and compressed paths must stay excluded from generic iomap paths unless full support exists.
