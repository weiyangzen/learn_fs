# File Research: sources/os/linux/linux/fs/jffs2/xattr.c

## Purpose
Implements the JFFS2 extended-attribute subsystem: xattr datum caching, xattr reference nodes, mount-time reconstruction, VFS get/set/list operations, and garbage-collection support for xattr flash nodes.

## Main Concepts
- `jffs2_xattr_datum` represents a unique xattr name/value payload stored in a raw `JFFS2_NODETYPE_XATTR` flash node.
- `jffs2_xattr_ref` links an inode cache to an xattr datum through raw `JFFS2_NODETYPE_XREF` nodes.
- Datums are hash-indexed by prefix/name/value so identical xattrs can be shared by multiple refs.
- Refs are sequence-numbered; the low bit is `XREF_DELETE_MARKER`, so newer ref/delete records win during mount reconstruction.
- `c->xattr_sem` protects logical xattr structures; `c->erase_completion_lock` protects raw-node chains and dead lists.

## Key Functions
- `xattr_datum_hashkey()` combines CRC32 of prefix/name and prefix/value for the datum cache key.
- `do_verify_xattr_datum()` reads a raw xattr node header from flash, validates node CRC, magic, nodetype, length, xid, and version, then converts unchecked raw refs to usable refs.
- `do_load_xattr_datum()` reads name/value bytes, validates `data_crc`, installs `xname`/`xvalue`, inserts the datum into `c->xattrindex`, and may trigger cache reclamation.
- `load_xattr_datum()` verifies unchecked datums before loading full value data.
- `save_xattr_datum()` writes a raw xattr node, increments `xd->version`, sets CRC fields, and registers a pristine physical node ref.
- `create_xattr_datum()` reuses an equivalent cached datum or creates/writes a new one with a fresh xid.
- `unrefer_xattr_datum()` decrements refcount, unloads cached data, marks dead datums, and places reclaimable nodes on `xattr_dead_list`.
- `verify_xattr_ref()` reads raw xref nodes during build, validates CRC/type/length, loads inode/xid/sequence data, and marks unchecked raw refs usable.
- `save_xattr_ref()` writes normal or delete-marker xref nodes and advances `highest_xseqno` by two.
- `create_xattr_ref()` writes a new xref and chains it onto `ic->xref`.
- `delete_xattr_ref()` marks a ref dead, records ino/xid for delete-node persistence, moves it to `xref_dead_list`, and unreferences the datum.
- `check_xattr_ref_inode()` lazily loads refs for an inode, removes corrupt datums, and resolves duplicate prefix/name refs by keeping the newest xseqno.
- `jffs2_build_xattr_subsystem()` reconstructs all xattr state after scanning in three phases: merge duplicate xrefs, bind live refs to inode caches and datums, and classify unchecked/orphan datums.
- `jffs2_setup_xattr_datum()` is the scanner-side insertion path for discovered xattr datums.
- `jffs2_listxattr()`, `do_jffs2_getxattr()`, and `do_jffs2_setxattr()` implement VFS-visible list/get/set semantics.
- `jffs2_garbage_collect_xattr_datum()` and `jffs2_garbage_collect_xattr_ref()` rewrite live xattr/xref nodes during GC.
- `jffs2_verify_xattr()` forces verification of unchecked datums before GC can safely reclaim related blocks.
- `jffs2_release_xattr_datum()` and `jffs2_release_xattr_ref()` free dead in-memory objects once their raw-node chains have been fully reclaimed.

## VFS Behavior
- `jffs2_xattr_handlers[]` exports user, optional security, and trusted handlers.
- `jffs2_xattr_prefix()` maps on-flash JFFS2 xattr prefixes to Linux handler prefixes and suppresses entries the caller is not allowed to list.
- `listxattr` and `getxattr` first call `check_xattr_ref_inode()` to normalize duplicate refs and purge corrupt refs.
- Read-side get/list can upgrade from `down_read()` to `down_write()` when a datum must be loaded or a corrupt ref must be removed.
- `setxattr` reserves flash space for the xattr datum first, writes/reuses a datum, then reserves/writes the xref. Replacing an existing xattr writes a new ref and deletes the old ref only after the new ref succeeds.
- Removing an xattr is encoded by writing a delete-marker xref before moving the old ref to the dead list.

## Mount and Corruption Handling
- Mount build deduplicates multiple refs for the same `(ino, xid)` by keeping the highest sequence and chaining older raw nodes behind it.
- Orphan xrefs, refs to missing/deleted inodes, refs to missing datums, and explicit delete markers are moved to `xref_dead_list`.
- Orphan datums with zero refs are marked `JFFS2_XFLAGS_DEAD` and left for verification/GC.
- CRC or structural validation failures mark datums invalid and cause callers to delete related refs when possible.
- The file uses a convention where negative return values are retryable/recoverable I/O or allocation errors, while positive `JFFS2_XATTR_IS_CORRUPTED` indicates unrecoverable corruption requiring logical deletion.

## Dependencies
- Uses JFFS2 raw-node APIs from `nodelist.h`: flash read/write, reservation, physical node refs, obsoletion, raw ref flags, and inode caches.
- Uses Linux xattr and POSIX ACL handler infrastructure.
- Relies on `jffs2_xattr_datum` and `jffs2_xattr_ref` definitions from `xattr.h`.

## Notable Details
- Cached xattr payload memory is capped by `xdatum_mem_threshold`, defaulting to 32 KiB.
- Reclamation uses a rotating hash-bucket index and a HOT bit: first pass cools hot datums, later passes unload non-bound cold datums.
- `JFFS2_XFLAGS_BIND` temporarily protects a datum from reclamation while another datum is being loaded for comparison.
- `save_xattr_ref()` assumes live refs have valid `ic` and `xd`; dead refs use stored `ino` and `xid`.
- Flash reservation is explicitly completed after each datum/xref write path.
