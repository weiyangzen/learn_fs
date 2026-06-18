# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hammer/hammer_disk.h

## Role

Defines the HAMMER1 on-disk format: fixed sizes, offset encoding, zones, blockmaps, UNDO/REDO FIFO records, volume headers, record/object types, inode payloads, directory entries, PFS metadata, snapshots, and config records.

## Format Foundations

- HAMMER uses 16 KiB filesystem buffers through `HAMMER_BUFSIZE`.
- File data at or beyond the 1 MiB demarc uses 64 KiB xbufs.
- Per-volume storage uses 52 offset bits; per-filesystem logical capacity is 60 bits, with top offset bits used for zones.
- `hammer_tid_t` is a 64-bit transaction id, usually synchronized to time.
- `hammer_off_t` is a 64-bit encoded address containing zone, optional volume number, and offset.

## Zone Encoding

The header defines zones for raw volume, raw buffer, undo, freemap, B-tree, metadata, large data, small data, and unavailable space. Helper macros test zone type, encode/decode zone and volume bits, and translate addresses into zone-2/raw-buffer addressing.

Important zone behavior:

- Zones 8 through 15 are record/data/meta classifications but usually carry a zone-2 physical address.
- The freemap is the only full two-layer blockmap user.
- Data-zone helpers distinguish large and small data by data length.

## Big-Block and Blockmap Layout

- HAMMER big-blocks are 8 MiB.
- The blockmap is a two-layer map: layer1 has 18 bits of fanout, layer2 has 19 bits, and big-block offset contributes 23 bits, totaling 60 bits.
- `struct hammer_blockmap` stores physical offset, first/next/alloc offsets, and CRC.
- `struct hammer_blockmap_layer1` tracks free big-block count and layer2 location.
- `struct hammer_blockmap_layer2` tracks zone, append offset, signed `bytes_free`, and CRC.
- Version 5 changed `bytes_free` to signed to allow deduplication to drive accounting below zero.

## UNDO/REDO FIFO

- FIFO entries use `hammer_fifo_head` and `hammer_fifo_tail` with signatures, type, aligned size, sequence number, and CRC.
- Version 4 reduced undo alignment to 512 bytes so each sector has a header and recovery can identify missing sectors.
- `hammer_fifo_undo` records raw metadata updates.
- `hammer_fifo_redo` records logical file writes/truncates for fast fsync semantics.
- REDO flags include write, truncation, write/trunc termination, and sync markers.
- Recovery semantics distinguish backward UNDO processing from forward REDO replay and REDO termination filtering.

## Volume Header

`struct hammer_volume_ondisk` contains:

- HAMMER signature, physical volume layout offsets, filesystem UUIDs, label, volume number/count, version, CRC, flags, and root volume id.
- Root-volume-only statistics such as big-block counts, inode count, B-tree root offset, and next transaction id.
- Cached blockmaps for all zones.
- The direct undo FIFO big-block array.

Version constants define minimum, default, work-in-progress, and maximum supported formats. Version notes include directory entry layout, snapshot layout, undo/flush changes, dedup, directory hash algorithm changes, and faster CRC support.

## Record and Object Types

Record types include inode, data, directory entry, DB, extended attributes, fixed attributes, PFS management, snapshot management, and cleanup config. Object types map HAMMER objects to directory, regular file, DB file, FIFO, device, symlink, PFS root, and socket semantics.

## Inode and Namespace Data

- `struct hammer_inode_data` stores version, mode, flags, device ids, ctime, parent object id, uid/gid UUIDs, object type, capability flags, link count, size, inline symlink space, mtime, and atime.
- `HAMMER_INODE_CRCSIZE` excludes mtime and atime from the inode data CRC, enabling special timestamp update paths.
- Directory entries store target object id, localization, and non-null-terminated name bytes.
- Symlink overflow data uses fixed records.
- Directory localization can use inode-localized entries depending on inode capability flags.

## PFS, Snapshot, and Config Records

- `struct hammer_pseudofs_data` stores mirror sync TIDs/timestamps, shared and unique UUIDs, flags, label, snapshot path, and prune policy.
- PFS flags distinguish slave and deleted states.
- HAMMER supports up to 65,536 pseudo-filesystems.
- Snapshot records store a TID key, timestamp, label, and reserved fields.
- Config records store cleanup configuration text and are not mirrored.

## Research Notes

This header is the durable HAMMER1 ABI. Most higher-level code in this group depends on these constants for locking, flushing, dedup accounting, recovery, and object interpretation.
