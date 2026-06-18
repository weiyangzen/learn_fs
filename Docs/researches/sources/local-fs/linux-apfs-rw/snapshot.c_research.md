# File Research: sources/local-fs/linux-apfs-rw/snapshot.c

## Purpose

`snapshot.c` implements snapshot creation and snapshot mount switching for APFS volumes. It creates a physical snapshot copy of the volume superblock, writes snapshot metadata/name records, rotates the live extent-reference tree, updates omap snapshot state, and maps snapshot superblocks for read-only snapshot mounts.

## Snapshot Creation

`apfs_ioc_take_snapshot()` handles `APFS_IOC_CREATE_SNAPSHOT`. It requires the ioctl on the root directory inode, checks owner/capability permissions with kernel-version-specific APIs, takes a write reference on the mount, copies the snapshot name from userspace, rejects unterminated or overlong names, and delegates to `apfs_do_ioc_take_snapshot()`.

`apfs_do_ioc_take_snapshot()` starts a regular transaction, checks that the name is unused, flushes all dirty inode metadata, copies the current volume superblock, creates snapshot metadata and name records, creates a new live extent-reference tree, updates omap snapshot tracking, increments the volume snapshot count, forces a commit, and aborts on failure.

## Metadata Records

- `apfs_create_superblock_snapshot()` allocates a new block, copies the current volume superblock, makes the snapshot superblock a physical FS object, clears the snapshot's omap oid, extentref tree oid, and snapshot metadata tree oid, and marks the buffer for checksum.
- `apfs_create_snap_metadata_rec()` inserts a metadata record keyed by current xid. The value stores the old extent-reference tree oid/type, snapshot superblock oid, create/change times, generated snapshot inode number, and null-terminated snapshot name.
- `apfs_create_snap_name_rec()` inserts a name record keyed by snapshot name and valued by current xid.
- `apfs_create_snap_meta_records()` CoWs the snapshot metadata tree root and updates the live volume superblock to point at the new root.

## Omap Snapshot Updates

`apfs_update_omap_snap_tree()` ensures the omap snapshot tree exists, CoWs its root, and inserts the current xid. `apfs_update_omap_snapshots()` CoWs the volume omap object, increments snapshot count, records the most recent snapshot xid, and updates the snapshot tree oid.

## Snapshot Mounting

`apfs_switch_to_snapshot()` is called during read-only mounting when `snap=` is set. It reads the live snapshot metadata tree, resolves the snapshot name to xid, resolves the xid to the snapshot superblock oid, unmaps the current live volume superblock, and maps the snapshot superblock by physical block number.

`apfs_snap_sblock_from_query()` rejects dataless snapshot metadata with `-EOPNOTSUPP`, so unknown dataless snapshot layouts are not mounted.

## Invariants And Risks

- Snapshot creation intentionally commits if the requested name already exists, because no modifications were made yet.
- Snapshot mounts are forced read-only by mount handling in `super.c`.
- Dirty inode metadata is flushed before snapshot layout changes to keep snapshot setup stable.
- Snapshot superblocks do not contain nested snapshot metadata and share omap state with the current volume.
- Failure after mutations relies on transaction abort and read-only fallback rather than fine-grained rollback.

## Test Focus

Test ioctl permission checks, mountpoint-only enforcement, name length and duplicate handling, transaction abort on each creation phase, snapshot metadata/name lookup, snapshot mount by name, dataless snapshot rejection, and consistency of omap snapshot counters and volume snapshot counts.
