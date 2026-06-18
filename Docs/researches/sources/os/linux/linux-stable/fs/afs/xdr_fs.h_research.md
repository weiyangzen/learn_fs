# File Research: sources/os/linux/linux-stable/fs/afs/xdr_fs.h

## Scope

Defines AFS fileserver XDR structures and constants for file status and directory page/block/entry layout.

## API Surface

- `struct afs_xdr_AFSFetchStatus` mirrors AFS fetch-status wire fields, including low/high size and data-version pieces, access masks, mode, parent FID, timestamps, lock count, and abort code.
- Directory constants define hash-table size, 32-byte dirent slots, 2048-byte blocks, blocks per page, slot/block limits, and reserved block counts.
- `union afs_xdr_dirent`, `struct afs_xdr_dir_hdr`, `union afs_xdr_dir_block`, and `struct afs_xdr_dir_page` describe packed directory storage.
- `afs_dir_calc_slots()` computes standardized dirent slot count from a filename length, including the historical first-slot size miscalculation.

## Dependencies And Risks

Directory parsing/editing code depends on these packed layouts and constants matching AFS on-disk/wire directory format. The slot calculation intentionally preserves protocol-compatible behavior even though the physical first slot has more name bytes.
