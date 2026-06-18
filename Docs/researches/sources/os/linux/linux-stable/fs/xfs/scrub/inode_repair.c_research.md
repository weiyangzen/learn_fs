# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/inode_repair.c

This file repairs inode record problems. It has two major regimes: raw dinode repair for inodes that cannot pass verifiers and be loaded, followed by live incore inode repair once `iget` succeeds.

Repair state:
- `struct xrep_inode` stores the saved `xfs_imap`, scrub context, block/extent counts discovered from rmap, sick masks for zapped metadata, ACL-zap state, and an inode scanner used to infer file type from directory entries.

Raw dinode repair:
- `xrep_setup_inode` stores the imap from setup when `iget` failed.
- `xrep_dinode_buf_core` and `xrep_dinode_buf` repair inode cluster buffer verifier requirements: magic, version, next-unlinked field, and CRC.
- `xrep_dinode_header` repairs invariant inode fields such as magic, version, inode number, UUID, and generation.
- `xrep_dinode_find_mode` scans directories with `xchk_iscan` to infer file type from dirent ftypes when mode bits are garbage.
- `xrep_dinode_mode` converts unrecognized modes to a conservative root-owned file type and marks ACLs for zapping.

Fork and size repair:
- `xrep_dinode_count_rmaps` counts this inode’s data, realtime, and attr blocks/extents from data-device and realtime rmap btrees.
- `xrep_dinode_check_dfork` and `xrep_dinode_check_afork` detect fork formats that would fail ifork verifiers or formatters.
- `xrep_dinode_zap_dfork` resets bad data forks to a safe format and marks bmbtd zapped.
- `xrep_dinode_zap_afork` empties attr forks, removes access permissions, clears IDs, and marks bmbta zapped.
- `xrep_dinode_zap_symlink` and `xrep_dinode_zap_dir` create minimal salvage structures for invalid local symlinks/directories.
- `xrep_dinode_ensure_forkoff` adjusts fork layout so later bmap repair can recreate mappings when rmap found extents.
- `xrep_dinode_core` writes the repaired raw dinode, retries `iget`, commits the transaction, attaches quota state, locks the live inode, and marks zapped sick flags.

Live inode repair:
- `xrep_inode_blockcounts` recounts fork mappings and updates extent counts and `i_nblocks`.
- `xrep_inode_ids` repairs invalid UID/GID/project IDs and schedules quotacheck when quotas are enabled.
- `xrep_inode_timestamps` clamps invalid nanoseconds.
- `xrep_inode_flags` clears impossible flag combinations.
- `xrep_inode_dir_size` derives directory size from extents or shortform data.
- `xrep_inode_pptr` ensures parent-pointer-capable files have an attr fork when required.
- `xrep_inode_extsize` and `xrep_inode_cowextsize` clear invalid realtime-related extent hints.
- `xrep_inode_unlinked` reconciles link count with the incore unlinked list.

Main entry:
- `xrep_inode` first repairs raw dinode verifier failures if `sc->ip` is absent, then joins the live inode to the transaction, repairs corrupt fields, clears reflink flags when possible, reconnects unlinked list state, and finishes deferred work.

Important invariants:
- Raw repair is conservative and may intentionally zap damaged forks so higher-level bmap, dir, symlink, or xattr repair can recover later.
- Rmapbt is required for reconstructing block and extent counts during raw repair.
- Bad ACL-bearing attr forks cause permissions and ownership to be restricted.

Risks and edge cases:
- Directory scans to infer mode can return busy; the repair defers rather than forcing unsafe progress.
- If data and realtime extents both exist for one inode, repair treats that as corruption.
- Zapping forks can temporarily leak or orphan metadata until follow-up repair phases run.
