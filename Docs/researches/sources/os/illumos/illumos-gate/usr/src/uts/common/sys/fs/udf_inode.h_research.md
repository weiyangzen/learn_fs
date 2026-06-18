# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/udf_inode.h

## Role

Defines illumos UDF in-core filesystem, partition, map, inode, extent, locking, permission, allocation, and exported helper interfaces. It connects UDF disk-format descriptors from `udf_volume.h` to VFS/vnode operations and block allocation code.

## Key Structures

- `struct udf_fid` is the UDF fid overlay containing partition number, ICB logical block number, and low unique-id bits.
- `struct ud_part` tracks UDF partition access mode, start/length, free/unallocated tables or bitmaps, free-block counts, and a small metadata allocation cache.
- `struct ud_map` describes normal, virtual partition, or sparable partition mapping, including VAT tables and sparing-table buffers.
- `struct udf_vfs` is per-mounted-UDF state: VFS/dev/root links, flags, media type, block sizing shifts, partitions/maps, free/total blocks, unique-id and file/dir counts, descriptor locations, cached primary/logical/integrity descriptors, root ICB, and locks.
- `struct icb_ext` stores one in-core allocation extent: flags, partition, block, file offset, byte count, and debug markers.
- `struct ud_inode` is the UDF inode state with hash/free links, vnode/dev/vfs links, `i_rwlock`, `i_contents`, extent arrays, continuation extents, file metadata, timestamps, delayed-write state, mapping state, device IDs, embedded-data offsets, and markers.

## Macros and Semantics

Defines block math (`blkoff`, `lblkno`, `fsbtodb`, `blkroundup`), vnode/inode conversions (`VTOI`, `ITOV`), UDF media/clean flags, ICB extent flags (`IB_UN_REC`, `IB_UN_RE_AL`, `IB_CON`), inode flags (`IUPD`, `IACC`, `IMOD`, `ICHG`, etc.), UDF permission conversion macros, sync modes, inode hash sizing, `UDF_HOLE`, and tracing support.

## Locking and Interfaces

Lock annotations specify `udf_vfs::udf_lock` protection for mutable free-space and clean-state fields, and `ud_inode::i_contents`/`i_tlock` protection for inode metadata and delayed-write state. The declared function surface spans UDF mount updates, vnode read/write helpers, inode lifecycle, allocation, volume translation, time conversion, tag verification, Unicode compression, directory operations, and bmap extent manipulation.

## Risk Notes

This is a central ABI and internal contract header. Errors in block-shift math, extent flags, permission conversions, or lock ordering can corrupt UDF allocation metadata or expose stale vnode/inode state.
