## sources/user-network-fs/nfs-ganesha/src/FSAL/localfs.c

### Purpose
`localfs.c` tracks locally mounted POSIX filesystems for FSALs that can host local filesystems. It scans mount tables, computes stable FSIDs/devices, maintains lookup indexes, builds parent/child mount topology, resolves export roots, claims/unclaims filesystems for FSAL exports, and exposes a DBus cache view when enabled.

### Important APIs, Types, And Functions
Path and index helpers include `open_dir_by_path_walk`, `re_index_fs_fsid`, `re_index_fs_dev`, `change_fsid_type`, `lookup_fsid`, `lookup_dev`, and locked variants. Scan/build helpers include `populate_posix_file_systems`, `posix_get_fsid`, `posix_create_file_system`, optional `posix_create_fs_btrfs_subvols`, `posix_find_parent`, and `path_is_subset`. Export lifecycle APIs include `resolve_posix_filesystem`, `claim_posix_filesystems`, `release_posix_file_system`, `release_posix_file_systems`, `unclaim_child_map`, `unclaim_all_filesystem_maps`, `get_fs_first_export_ref`, `unclaim_all_export_maps`, `is_filesystem_exported`, and `str_claim_type`. DBus support includes `posix_showfs` and `dbus_cache_init`.

### Control Flow
`resolve_posix_filesystem` stats an export path with configured retry/delay, rescans mount state with `populate_posix_file_systems`, then claims the matching root filesystem. Scanning initializes AVL indexes once, releases unclaimed top-level filesystems, reads `MOUNTED`, filters unsupported or dangerous filesystem types, stats candidate mount points, creates filesystem records, and builds parent links. `posix_create_file_system` fills path/device/type, computes FSID from device, blkid UUID, statfs fsid, or export override, inserts into fsid and dev AVL indexes, links into the global list, and optionally discovers btrfs subvolumes. Claiming finds the root filesystem by device or configured FSID override, then `process_claim` recursively claims root/subtree/child filesystems while resolving conflicts with existing root, subtree, and child claims.

### State And Persistence
Global runtime state includes `fs_lock`, `posix_file_systems`, `fs_initialized`, `avl_fsid`, `avl_dev`, and optional blkid cache. Each `fsal_filesystem` stores path, device, type, fsid/dev keys, parent/children, export maps, claim counters, owning FSAL, unclaim callback, and private data. State is in-memory and rebuilt from mount tables; backend filesystems are persistent but not modified except through FSAL claim/unclaim callbacks.

### Dependencies And Integration Points
It depends on local FSAL headers, export state, idmapper DBus functions, POSIX mount/stat APIs, blkid/uuid when enabled, btrfsutil when enabled, `fsal_convert` for device mapping, and core parameters such as `fsid_device`, `fsid_override`, `resolve_fs_retries`, and `resolve_fs_delay`. FSAL implementations pass `claim_filesystem_cb` and `unclaim_filesystem_cb` to attach backend-specific data to filesystem records.

### Risks
Mount scanning must avoid hangs; NFS/autofs and pseudo filesystems are filtered before `stat`, but new problematic filesystem types may need additions. Claim conflict logic is complex and order-sensitive for overlapping exports; comments acknowledge spurious warnings depending on export ordering. FSID derivation can collide; duplicate handling updates device/type in some cases and drops duplicates in others. `change_fsid_type` compresses or truncates identifiers for alternate formats, creating collision risk. All registry mutations rely on `fs_lock`; callbacks invoked while locked must avoid deadlocks. `open_dir_by_path_walk` rejects `..` and uses `O_NOFOLLOW`, but path parsing edge cases need coverage.

### Test Signals
Tests should cover path walking with absolute/relative roots, symlinks, repeated slashes, and `..`; mount scan filtering; FSID derivation with device, statfs, blkid UUID, and override; duplicate fsid/dev insertion; parent-child topology; resolve retry behavior; root/subtree/child claim conflicts across same and different FSALs; unclaim recursion; lookup by fsid/dev under locks; btrfs subvolume discovery when enabled; and DBus `showfs` output.
