# sources/user-network-fs/samba/source3/modules/vfs_fileid.c

## Purpose
`vfs_fileid.c` customizes Samba `struct file_id` creation for share-mode and byte-range-lock databases, supporting stable or cluster-aware device identifiers and special nolock external ids.

## Important APIs, Types, And Functions
`struct fileid_handle_data` stores the selected mapping function, allow/deny lists, cached mount entries, and nolock configuration. Mapping functions include fsname hash, fsid, hostname+device hash, and next-module delegation. `/etc/mtab` entries are loaded into `struct fileid_mount_entry`. Nolock rules use `struct fileid_nolock_inode` and `fileid_mapping_nolock_extid()`.

## Control Flow
Connect delegates, allocates state, selects `fileid:algorithm` with legacy `fileid:mapping` fallback, copies mount filters, reads nolock options, resolves configured nolock paths, and stores handle data. File-id creation calls the mapping function and applies a derived extid if the inode matches nolock rules.

## State And Persistence
State is per handle, including cached mount table entries. Behavior depends on current `/etc/mtab`, hostname, CTDB VNN, process id modulo slots, and smb.conf. Nothing is persisted by the module.

## Dependencies And Integration Points
The module depends on mount table APIs, `stat`, `statfs`, hostname, CTDB `get_my_vnn()`, Samba file-id VFS hooks, loadparm lists, and locking/share-mode consumers of file ids.

## Risks
File-id instability can break locking semantics. Hash collisions are possible. `/etc/mtab` may be container-specific or stale. Some algorithms force nolock extids broadly. `nolock_max_slots` uses process id distribution. Allow/deny filters are exact string matches. Legacy `nolockinode` ignores device.

## Test Signals
Test all algorithms, mount filters, mtab reloads, `/dev/` stripping, fsid packing, hostname failure, nolock all-inodes/all-dirs/rootdir/path/legacy modes, max-slot extid distribution, next-module delegation, and reconnect stability.
