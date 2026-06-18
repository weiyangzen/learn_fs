# File Research: sources/os/linux/linux/fs/ntfs/aops.c

## Role

This file defines NTFS address-space operations and page-cache handling for regular NTFS data and MFT mappings. It uses iomap for normal buffered reads, readahead, writeback, bmap, and swap activation.

## Read Path

`ntfs_read_folio()` handles page-cache folio reads. It rejects unsupported encrypted attributes with `-EOPNOTSUPP`, delegates compressed non-resident streams to `ntfs_read_compressed_block()`, and otherwise calls `iomap_read_folio()` with NTFS iomap read ops.

The custom read end I/O handler zeroes the part of a folio past `initialized_size` when a bio crosses that boundary, then completes iomap folio read accounting.

## Readahead

`ntfs_readahead()` skips resident files and compressed files, then calls `iomap_readahead()` for non-resident uncompressed mappings.

## Block Mapping

`ntfs_bmap()` maps logical filesystem blocks to physical device blocks for suitable non-resident, unencrypted, non-MST-protected `$DATA` attributes.

It checks initialized size and file size to report holes, looks up the runlist under the runlist read lock, handles error LCNs, converts clusters to block units, and returns 0 for holes/errors/truncation cases.

The function documents the usual `bmap()` ambiguity where physical block 0 cannot be distinguished from hole/error.

## Writeback

`ntfs_writepages()` rejects volume shutdown, ignores resident files, rejects encrypted files, and uses `iomap_writepages()` with NTFS writeback ops.

MFT writeback uses a separate `ntfs_mft_writepages` operation in the MFT address-space table.

## Swap Activation

`ntfs_swap_activate()` delegates swapfile validation/mapping to `iomap_swapfile_activate()` using NTFS read iomap ops.

## Address-Space Tables

`ntfs_aops` provides normal NTFS mapping operations: read, readahead, writepages, dirty, bmap, migration, partial uptodate, error removal, release, invalidate, and swap activation.

`ntfs_mft_aops` is similar but uses MFT-specific writepages and omits swap activation.

## Design Notes

The file is the bridge between NTFS runlist/attribute semantics and Linux's iomap/page-cache APIs, with explicit exclusions for encrypted and compressed paths that require special handling.
