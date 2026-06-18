# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/hsfs/hsfs_node.c

## Role

Implements HSFS vnode/hsnode lifecycle, directory lookup, directory record parsing, ISO/Joliet/Rock Ridge name handling, and hsnode hash/free-list management.

## Node Cache And Hashing

- `hs_init_hsnode_cache()` and `hs_fini_hsnode_cache()` manage the `hsfs_hsnode_cache` kmem cache.
- `hs_hsnode_cache_reclaim()` purges DNLC entries and frees per-mount free-list hsnodes during memory pressure.
- `hs_getfree()` allocates or reuses hsnodes, invalidating cached pages and freeing symlink storage before reinitialization.
- `hs_findhash()` finds and reactivates cached hsnodes by inode; for `HS_DUMMY_INO`, it additionally matches directory LBN and offset.
- `hs_makenode()` normalizes directory entry location, chooses node id from RRIP inode, extent LBN, or dummy inode, creates/reuses vnode, installs `hsfs_vnodeops`, handles device nodes through `specvp()`, and inserts into the hash.
- `hs_freenode()` either fully frees vnode/hsnode resources or places nodes on the per-filesystem free list.
- `hs_synchash()` invalidates pages and frees all hsnodes during unmount, returning busy if referenced nodes remain.
- `hs_remakenode()` rereads a directory record by LBN/offset to reconstruct a vnode for `VFS_VGET`.

## Directory Lookup

- `hs_dirlook()` checks directory execute access, consults DNLC, prepares a comparison name based on RRIP/ISO/Joliet policy, then scans directory data with `fbread()` and `process_dirblock()`.
- Supports wraparound searching from the previous successful offset (`hs_offset`) for locality.
- Rejects ISO/Joliet lookup for raw `\1` names because `\1` represents `..` on disk.
- Adds successful results to DNLC when enabled.

## Directory Record Parsing

- `hs_parsedir()` parses High Sierra and ISO/Joliet directory records into `hs_direntry`.
- Sets extent LBN, size, XAR length, interleave data, type, mode, link count, uid/gid, dates, protection, inode, and symlink.
- Invokes `parse_sua()` when SUSP is implemented, allowing RRIP fields to override names, modes, times, devices, links, and relocation.
- Validates directory entry length, filename length, interleave constraints, multi-volume set expectations, and unsupported type bits.
- Falls back to ISO/Joliet name copying when RRIP did not change the name.

## Name Handling

- `hs_namecopy()` converts ISO names to Unix form, handles `.`/`..`, optional version stripping, lowercase mapping, and trailing-space trimming.
- `hs_jnamecopy()` converts Joliet UCS-2 names to UTF-8 and reports truncation as a negative length.
- `hs_uppercase_copy()`, `hs_iso_copy()`, and `hs_joliet_cp()` prepare lookup comparison names.
- `hs_ucs2_2_utf8()` implements UCS-2 to UTF-8 conversion.
- `strip_trailing()` and `hs_namelen()` support defensive warnings and version-aware length checks.

## Directory Block Processing

- `process_dirblock()` validates each directory entry boundary and name length, obtains RRIP names when present, handles ISO version stripping and strict ISO ordering, compares names, parses matching entries, releases fbuf before node creation, and returns `FOUND_ENTRY`, `WENT_PAST`, or `HIT_END`.
- The function contains hardening against malformed or malicious media: invalid short records, overlong names, bad RRIP symlink allocations, and sector boundary inconsistencies.

## Dependencies And Interactions

- Uses HSFS volume structures, vnode/page cache APIs, DNLC, SUSP/RRIP parsers, and VM page invalidation.
- Works with `hsfs_vfsops.c` for mount/unmount and `hsfs_vnops.c` for page invalidation callbacks such as `hsfs_putapage()`.
