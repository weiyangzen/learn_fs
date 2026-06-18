# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/zfs_fuid.c

Implements ZFS FUID support: compact persistent encoding of POSIX IDs and SID-like domain/rid identities used for owners, groups, and ACL ACEs. It maintains per-filesystem domain tables, maps between FUIDs and illumos uid/gid values, records new FUID domains for logging, and supports replay.

On disk, the FUID table is a packed XDR nvlist containing an array of domain records with index, domain string, and offset. `zfs_fuid_table_load()` reads the table object, unpacks the nvlist, and builds two AVL trees keyed by index and domain. `zfs_fuid_sync()` serializes the current AVL contents back to a DMU object, creating `ZFS_FUID_TABLES` in the master node if needed, and stores the packed size in the object bonus buffer.

`zfs_fuid_avl_tree_create()`, `zfs_fuid_table_destroy()`, `zfs_fuid_idx_domain()`, `zfs_fuid_find_by_domain()`, and `zfs_fuid_find_by_idx()` manage the in-memory domain table. New domains are assigned monotonically increasing indexes and set `zfsvfs->z_fuid_dirty`, making callers responsible for reserving transaction space and syncing.

Mapping functions include `zfs_fuid_map_id()` and `zfs_fuid_map_ids()`, which convert FUIDs to uid/gid values through `kidmap` when the FUID index is nonzero. `zfs_fuid_create_cred()` creates owner/group FUIDs from credentials, preferring credential SIDs for ephemeral IDs and falling back to plain POSIX IDs or nobody when necessary. `zfs_fuid_create()` creates FUIDs for explicit chown/chgrp or ACL ACE IDs, querying idmap for domain/rid outside replay and consuming logged replay FUID state during replay.

`zfs_fuid_node_add()` builds a `zfs_fuid_info_t` side structure recording domains and FUIDs created during an operation. That structure is used by ZIL logging and replay to preserve the exact domain/rid mapping for owners, groups, and ACL ACEs. `zfs_fuid_info_alloc()` and `zfs_fuid_info_free()` manage its lists and optional replay domain table.

Credential membership helpers are optimized for hot ACL access checks. `zfs_fuid_is_cruser()` compares a FUID to the credential user, avoiding idmap calls when the credential already has a matching KSID. `zfs_user_in_cred()` checks the credential user and SID list for ACE user IDs. `zfs_groupmember()` checks primary group KSID, SID list, process groups, and finally POSIX group membership after FUID-to-gid mapping.

`zfs_fuid_txhold()` reserves the correct DMU transaction holds for syncing a dirty FUID table, handling both new-table creation and updates to an existing table object.

Key invariants: FUID index zero means a plain POSIX ID; empty domain maps to index zero/nobody-style fallback; domain AVL nodes are never removed while the filesystem is active; replay does not call idmap but consumes logged FUID information; callers that dirty domains must include FUID transaction holds and call `zfs_fuid_sync()`.
