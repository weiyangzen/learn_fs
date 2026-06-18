# File Research: sources/os/linux/linux/fs/xfs/scrub/inode_repair.c

Repairs inode records. It has two layers: raw dinode repair for verifier-failing inodes that cannot be loaded, and incore inode repair for inconsistencies that can be fixed after iget succeeds.

Main raw-dinode repair:
- `struct xrep_inode` stores saved `xfs_imap`, rmap-derived block/extent counts, sick bits to set after zapping, ACL-zap state, and scan state for recovering file type from directory entries.
- `xrep_setup_inode` saves the inode mapping produced by scrub setup.
- `xrep_dinode_buf_core` and `xrep_dinode_buf` fix inode-buffer verifier essentials: magic, version, CRC, and next-unlinked validity.
- `xrep_dinode_header` resets immutable header fields: magic, version, inode number, UUID, and generation.
- `xrep_dinode_find_mode` scans directories with `xchk_iscan` to infer file type from dirents when `di_mode` is garbage.
- `xrep_dinode_mode`, `xrep_dinode_nlinks`, `xrep_dinode_flags`, `xrep_dinode_size`, and `xrep_dinode_extsize_hints` repair verifier-sensitive core fields.
- `xrep_dinode_count_rmaps` scans data and realtime rmaps to infer blocks/extents owned by the inode.
- `xrep_dinode_check_dfork` and `xrep_dinode_check_afork` validate fork format and embedded fork contents enough for ifork verifiers.
- `xrep_dinode_zap_dfork`, `xrep_dinode_zap_afork`, `xrep_dinode_zap_symlink`, and `xrep_dinode_zap_dir` reset unrecoverable forks to safe minimal structures and mark zapped sickness.
- `xrep_dinode_ensure_forkoff` adjusts fork offset so existing/recoverable data and attr fork stubs can fit.
- `xrep_dinode_core` reads the inode cluster, fixes the raw dinode, writes/logs it, retries iget, commits, reopens transaction, attaches dquots, locks the inode, and propagates zapped sick bits.
- `xrep_dinode_problems` schedules quotacheck after rebuilding a badly damaged dinode.

Main incore repair:
- `xrep_inode_blockcounts` recomputes data/attr fork extent and block counters.
- `xrep_inode_ids` resets invalid uid/gid/project IDs and forces quota checks as needed.
- `xrep_inode_timestamps` clamps timestamps to valid nanosecond ranges and filesystem granularity.
- `xrep_inode_flags` clears invalid or contradictory inode flags.
- `xrep_inode_dir_size` repairs directory size from shortform bytes or last block extent.
- `xrep_inode_pptr` ensures an attr fork exists when parent pointers are enabled and the inode should have one.
- `xrep_inode_extsize` and `xrep_inode_cowextsize` clear invalid realtime-aligned hints.
- `xrep_inode_problems` applies incore fixes and logs the inode core.
- `xrep_inode_unlinked` reconciles link count with the incore unlinked list.
- `xrep_inode` orchestrates raw repair if needed, incore repair for corrupt or cross-corrupt results, reflink flag clearing, unlinked-list repair, and deferred-op finishing.

Important policy:
- Unknown or invalid mode is made a root-readable regular file unless directory entries reveal a better type.
- Zapping attr forks removes access bits and resets ownership because ACLs may have been lost.
- Data/attr forks are zapped only enough to make higher-level bmap, directory, symlink, or xattr repair possible later.
- If directory scanning for mode recovery hits temporary busy state, repair returns without continuing destructive changes.
