# File Research: sources/os/linux/linux/fs/xfs/scrub/inode.c

Scrubs inode core metadata. Setup carefully obtains a live inode or, if iget fails due to corruption, preserves enough AGI and inode mapping state for repair to fix the on-disk inode buffer.

Main flow:
- `xchk_prepare_iscrub` takes IOLOCK, allocates transaction, attaches dquots, and takes ILOCK.
- `xchk_install_handle_iscrub` installs a scrub-by-handle inode, rejects unsafe non-directory metadata-dir files from userspace, and prepares it.
- `xchk_setup_inode` handles opened-inode scrubs, scrub-by-handle validation, safe untrusted iget, retry under AGI lock, direct inobt mapping via `xfs_imap`, and repair setup for allocated but unloadable corrupt inodes.
- `xchk_dinode` validates dinode fields: mode, version, metatype, project ID support, uid/gid warnings, fork format, timestamps, size, nblocks, flags, extsize/cowextsize hints, nextents/anextents, forkoff, attr format, bigtime, and large extent count feature dependencies.
- `xchk_inode_xref_finobt` ensures finobt does not mark the loaded inode free.
- `xchk_inode_xref_bmap` compares fork extent counts and block counts against inode core counters.
- `xchk_inode_xref` checks backing block usage, finobt, rmap ownership, sharing, CoW staging, and fork counters.
- `xchk_inode_check_reflink_iflag` compares the reflink inode flag to actual shared data fork extents, marking preen or corruption.
- `xchk_inode_check_unlinked` verifies link count matches unlinked-list membership.
- `xchk_inode` converts the live inode to a disk-format dinode for checking, handles setup-detected unloadable corruption, performs reflink/unlinked checks, and cross-references.

Important behavior:
- Setup returns `-ENOENT` for free/missing inodes so scrub can skip them.
- If inobt says an inode is allocated but iget fails from corruption, setup leaves state for repair rather than marking corruption directly.
- Cross-reference checks are skipped after primary inode corruption to avoid noisy secondary reports.
