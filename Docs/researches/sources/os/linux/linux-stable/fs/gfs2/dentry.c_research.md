# File Research: sources/os/linux/linux-stable/fs/gfs2/dentry.c

## Purpose
Provides GFS2 dentry operations for clustered lookup coherency, GFS2 directory hashing, and dentry deletion decisions.

## Key Interfaces
- `gfs2_drevalidate()` validates cached dentries against the parent directory.
- `gfs2_dhash()` computes on-disk-compatible name hashes.
- `gfs2_dentry_delete()` drops dentries when iopen glocks are being demoted.
- `gfs2_dops` exports the dentry operation table.

## Control Flow And Behavior
Revalidation rejects RCU mode, accepts local/nolock mode immediately, otherwise takes the parent directory glock shared when not already held and checks whether the dentry still matches directory contents. Negative dentries are valid only if lookup returns `-ENOENT`.

## Dependencies
Uses GFS2 directory search/check helpers, glocks, lock module state, inode bad-state checks, and Linux dcache operations.

## Risks And Invariants
Clustered dentry validation must not proceed in RCU mode because it may need glock acquisition. Hashing must match the GFS2 on-disk directory hash.
