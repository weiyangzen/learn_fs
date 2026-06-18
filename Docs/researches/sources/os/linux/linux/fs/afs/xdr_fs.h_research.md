# File Research: sources/os/linux/linux/fs/afs/xdr_fs.h

## Scope

This header defines packed AFS fileserver XDR structures and directory-layout constants used for status decoding and AFS directory parsing/editing.

## APIs And Constants

- `struct afs_xdr_AFSFetchStatus` mirrors AFS FetchStatus wire fields, including type, link count, size/data-version split words, ownership, access masks, mode, parent FID parts, timestamps, group, sync counter, lock count, and abort code.
- Directory geometry constants define hash table size, dirent size, slots per block, block size, blocks per page, maximum slots/blocks, and reserved blocks.
- `union afs_xdr_dirent` describes the first directory entry slot and extended-name slots.
- `struct afs_xdr_dir_hdr`, `union afs_xdr_dir_block`, and `struct afs_xdr_dir_page` describe the on-wire directory block/page layout.
- `afs_dir_calc_slots()` computes directory-entry slot count using the standardized historical 16-byte first-name-slot calculation.

## Dependencies And Role

- Included by AFS directory and fileserver decoding code.
- Uses `PAGE_SIZE`, `__be16`, `__be32`, and packed layout annotations.

## Risks And Invariants

- Directory structures must match AFS on-disk/on-wire layout exactly.
- The slot calculation intentionally preserves a historical miscalculation; changing it would break interoperability.
- Directory block count per page assumes the AFS 2048-byte directory block size.
