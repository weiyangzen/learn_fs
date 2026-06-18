<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/mountd/rmtab.c -->
# sources/user-network-fs/nfs-utils/utils/mountd/rmtab.c

## Purpose

`rmtab.c` manages `rpc.mountd`'s remote mount table, recording which clients have mounted which exported paths and providing the MOUNT DUMP response list.

## Important APIs, types, and functions

Public functions are `mountlist_add`, `mountlist_del`, `mountlist_del_all`, and `mountlist_list`. Private `slink_safe_rename` preserves a symlinked rmtab path by renaming the temp file to the symlink target. `mountlist_freeall` releases cached RPC mountlist nodes.

## Control flow

Adds take an append lock, scan existing entries, increment count for duplicates, or append a new entry. Deletes take a write lock, stream existing entries to a temp file while decrementing/removing matches, and rename the temp file into place. UMNTALL canonicalizes the caller hostname, authenticates each path before removing it, and rewrites the table. Listing caches an in-memory mountlist until rmtab mtime changes.

## State and persistence behavior

Persistent state is the configured `rmtab.statefn` text file with client/path/count entries, guarded by `rmtab.lockfn` and rewritten through `rmtab.tmpfn`. HA callouts fire on mount and unmount count changes. The DUMP response list is cached statically in process memory.

## Dependencies and integration points

It depends on support `xio` rmtab helpers, file locks, host canonicalization, export authentication for UMNTALL, `ha-callout`, and `mountd.h`. `mountd.c` calls it after successful MNT and authenticated UMNT operations.

## Risks and edge cases

The symlink-safe rename follows only the destination symlink and trusts its target path. Cached mountlist invalidation uses mtime only. Reverse DNS during listing can fail and falls back to stored client text. If temp-file rewrite or rename fails, rmtab can become stale. Lock acquisition failures silently skip updates.

## Test signals

Tests should cover duplicate mount count increments, decrement-to-zero removal, symlinked rmtab paths, failed rename handling, UMNTALL auth filtering, reverse-resolve on/off, mtime cache reuse, allocation failures while listing, and HA callout arguments.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/mountd/rmtab.c -->
