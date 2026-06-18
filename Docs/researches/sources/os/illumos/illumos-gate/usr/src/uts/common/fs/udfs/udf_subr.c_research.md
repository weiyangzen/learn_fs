# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/udfs/udf_subr.c

## Purpose

Provides shared UDFS support routines: mounted-filesystem list management, partition address translation, directory offset-to-block conversion, UDF timestamp conversion, inode/superblock sync helpers, descriptor tag creation/verification, FID reading across block boundaries, CRC, UDF name compression/uncompression, safe block reads, and sticky-directory deletion checks.

## Main Entry Points

- `ud_vfs_add()` / `ud_vfs_remove()`: maintain the global mounted UDFS instance list.
- `ud_xlate_to_daddr()`: translate logical partition references into device blocks for normal, virtual, and sparable partition maps.
- `ud_ip_off2bno()`: map directory offsets to UDF logical block numbers for descriptor tag locations.
- `ud_dtime2utime()` / `ud_utime2dtime()`: convert between UDF timestamps and Unix `timespec32`.
- `ud_syncip()`, `ud_update()`, `ud_flushi()`, `ud_checkclean()`: flush inode/page/superblock state and mark clean volumes when possible.
- `ud_sbwrite()`: update and write the logical volume integrity descriptor.
- `ud_make_tag()` / `ud_verify_tag_and_desc()`: create and validate UDF descriptor tags, checksums, CRCs, locations, and selected metadata bounds.
- `ud_get_next_fid()`: read and validate a File Identifier Descriptor and name, including descriptors split across logical blocks.
- `ud_compress()` / `ud_uncompress()`: convert between UTF-8 names and UDF compressed Unicode names.
- `ud_bread()`: wrapper around `bread()` that retries if the buffer cache returns the wrong byte count.
- `ud_sticky_remove_access()`: enforce sticky-directory removal rules.

## Control Flow And State

Partition translation handles three map types. Normal maps add the partition start. Virtual maps use loaded VAT address arrays and return one block at a time. Sparable maps scan sparing table entries, remapping requests that intersect defective packet ranges while limiting returned contiguous counts to the remapped or pre-defect region.

The sync path builds a temporary list of vfs-locked UDFS instances, writes dirty superblocks, flushes inodes and buffers, and then revalidates that each filesystem is still mounted before checking whether it can be marked clean. `ud_icheck()` prevents clean marking while dirty, writer-locked, or unlinked referenced inodes remain.

Descriptor verification first checks tag ID and checksum. With descriptor verification enabled it also checks CRC length, descriptor CRC, tag location, FID length bounds, file-entry extended-attribute/allocation-descriptor bounds, and extended-attribute header bounds. This defensive checking protects directory and inode parsers from malformed media metadata.

Name compression converts UTF-8 into 8-bit or 16-bit UDF compressed Unicode. Uncompression maps invalid Unix names such as `.`/`..`, slash, NUL, or overlong names into safe names with appended CRC fragments. The UTF conversion code is explicitly Unicode 1.1-era and does not handle surrogate pairs.

## Dependencies

Depends on UDFS mount/inode globals, buffer cache, vnode page flushing, partition maps loaded by mount code, UDF descriptor structures, Solaris security policy hooks, and shared allocation/inode update routines.

## Risks

`ud_xlate_to_daddr()` returns zero on invalid translations, which can be ambiguous with real block zero unless callers validate context. `ud_ip_off2bno()` assumes directories have no holes and does not explicitly return `EINVAL` if no matching extent is found after a successful descriptor load. The global sync traversal intentionally uses vfs locks instead of a single long-held mount-list lock, so mount/unmount coordination relies on the revalidation pattern. Unicode conversion is not modern UTF-16 complete.
