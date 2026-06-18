# File Research: sources/os/bsd/dragonflybsd/sys/vfs/udf/udf_vnops.c

DragonFly UDF vnode operations implementation for the read-only filesystem.

Key responsibilities:
- Defines `udf_vnode_vops` with handlers for access, bmap, old lookup, getattr, ioctl, pathconf, read, readdir, readlink, reclaim, and strategy.
- Implements vnode hash helpers `udf_hashlookup`, `udf_hashins`, and `udf_hashrem` protected by the mount hash token.
- Implements `udf_allocv`, allocating a UDF vnode and downgrading the VX lock state for normal use.
- Converts UDF file-entry permissions and ICB flags to DragonFly `mode_t` in `udf_permtomode`.
- Implements read-only access checks through `vop_helper_access`.
- Converts UDF timestamps to `timespec` with leap-year handling and a 12-bit signed timezone offset.
- Implements `udf_getattr`, filling vnode attributes from UDF file entries, including fallback uid/gid handling for `0xffffffff`, directory-size normalization, block size, file id, link count, and timestamps.
- Implements `udf_read`, using `udf_readatoffset` and `uiomove` to read regular file data.
- Implements CS0 name translation and comparison helpers, using OSTA decompression and replacing non-8-bit Unicode characters with `.`.
- Implements directory stream helpers `udf_opendir`, `udf_getfid`, and `udf_closedir`; `udf_getfid` handles file identifier descriptors that span logical-block boundaries by assembling fragments into a temporary buffer.
- Implements `udf_readdir`, emitting `.` and `..`, skipping deleted entries, translating names, returning directory cookies when requested, and writing entries through `vop_write_dirent`.
- Implements `udf_lookup`, scanning directory FIDs, supporting lookup restart from `node->diroff`, handling `..`, returning `EROFS` for create/rename misses, and resolving matches through `udf_vget`.
- Implements `udf_strategy` and `udf_bmap`, translating vnode logical offsets to device offsets unless file data is embedded in the file entry.
- Implements `udf_readatoffset`, handling normal extent reads and embedded file-entry data.
- Implements `udf_bmap_internal`, supporting allocation strategy type 4, short and long allocation descriptors, embedded-data descriptors, and sparing-table remapping.
- Implements `udf_reclaim`, removing a vnode from the hash and freeing device references, copied file entry, and node memory.

Dependencies:
- Uses DragonFly VOP, buffer, uio, namei, dirent, iconv include surface, vnode locking, BIO strategy, and kernel malloc APIs.
- Uses UDF descriptor structures/macros from `ecma167-udf.h` and internal mount/node state from `udf.h`.
- Relies on OSTA Unicode decompression from `osta.c`.

Notable risks:
- The filesystem is read-only; create/rename through lookup return `EROFS`, and many mutation VOPs are absent.
- Unicode handling is deliberately incomplete and lossy for 16-bit characters, which affects lookup and readdir name fidelity.
- Directory FID parsing trusts length fields after limited checks; fragmented FID assembly has several bounds-sensitive paths.
- `udf_strategy` checks `nbio->bio_offset == NOOFFSET` before calling `udf_bmap_internal` but passes `bio->bio_offset`; this path is subtle because embedded data cannot be represented as a device block.
- `udf_bmap_internal` has limited allocation descriptor support and rejects strategy 4096 and extended descriptors.
- Timestamp conversion is explicitly approximate and ignores daylight savings and nanoseconds.
