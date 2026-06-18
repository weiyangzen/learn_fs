<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/nfsdcld/legacy.c -->
# sources/user-network-fs/nfs-utils/utils/nfsdcld/legacy.c

## Purpose

`legacy.c` migrates and cleans the older kernel NFSv4 recovery directory format for `nfsdcld` first-time upgrades.

## Important APIs, types, and functions

`legacy_load_clients_from_recdir` reads `/proc/fs/nfsd/nfsv4recoverydir`, opens the directory it names, prefixes each legacy entry with `hash:`, includes the NUL terminator, and inserts it into the current SQLite client table. `legacy_clear_recdir` reads the same proc file and removes each child directory after the first grace completes.

## Control flow

Both functions open the proc file, read a newline-terminated directory path, trim it, and iterate non-dot entries. Loading formats each entry into a bounded buffer and calls `sqlite_insert_client`. Clearing constructs full child paths and calls `rmdir`.

## State and persistence behavior

It reads kernel-advertised legacy recovery directory state and writes migrated records to `nfsdcld` SQLite. Cleanup removes legacy recovery subdirectories best-effort. Record counts are returned by incrementing the caller's integer.

## Dependencies and integration points

It depends on procfs nfsd recovery directory reporting, `sqlite_insert_client`, NFSv4 opaque limits from `cld.h`, and `xlog`. `sqlite_prepare_dbh` invokes migration when the database `first_time` parameter is set; `cld_gracedone` invokes cleanup after the first grace.

## Risks and edge cases

The code skips entries that exceed `NFS4_OPAQUE_LIMIT` after `hash:` prefixing. It assumes legacy entries are direct child directories and uses `rmdir`, so non-empty or non-directory entries remain. Proc-file reads require a newline; missing newline silently aborts.

## Test signals

Tests should cover missing proc file, invalid/no-newline path, empty recovery dir, dot entries, long names, sqlite insert failures, count increments, cleanup failures, and interaction with first-time migration from cltrack records.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/nfsdcld/legacy.c -->
