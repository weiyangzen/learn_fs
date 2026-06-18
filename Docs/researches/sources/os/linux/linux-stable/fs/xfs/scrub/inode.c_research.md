# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/inode.c

This file scrubs inode core metadata. It handles setup for live inode or by-handle inode scrubs, detects corrupt-on-load inodes, validates dinode fields, and cross-references inode state against allocation metadata and mappings.

Setup paths:
- `xchk_setup_inode` handles three cases:
  - scrub the open file’s inode
  - safely load a requested inode by handle
  - if iget fails due to corruption, lock AGI, verify inobt allocation, save imap for repair, and let `xchk_inode` report corruption
- Metadata directory non-directory inodes are rejected from direct userspace by-handle scrub.
- Internal sb-rooted metadata files are rejected on pre-metadir filesystems.

Core validation:
- `xchk_dinode` validates mode, inode version, metadir type, project id fields, UID/GID warnings, fork formats, timestamps, size, nblocks, flags, extent hints, fork offsets, attr format, and extent counters.
- `xchk_inode_flags` checks legacy di_flags against mode and feature constraints.
- `xchk_inode_flags2` checks reflink, DAX, bigtime, large extent count, and realtime/reflink compatibility.
- `xchk_inode_extsize` and `xchk_inode_cowextsize` validate extent size hints and issue warnings for admin-created realtime hint misalignment.

Cross-reference checks:
- `xchk_inode_xref` initializes AG metadata and verifies the inode block is used, finobt does not mark it free, rmap says it is inode-owned, and it is not shared or COW staging.
- `xchk_inode_xref_bmap` recounts fork extents/blocks and compares them with dinode counters.
- `xchk_inode_check_reflink_iflag` compares reflink flag state with shared extent discovery.
- `xchk_inode_check_unlinked` checks link count against the incore unlinked list.

Main scrub:
- `xchk_inode` marks corruption if setup could not load `sc->ip`, otherwise converts the incore inode to a disk dinode image, validates it, optionally checks reflink and unlinked state, and performs xrefs.

Important invariants:
- Inode scrub holds IOLOCK and ILOCK exclusively after setup.
- Inobt allocation status is trusted for detecting allocated-but-unloadable inodes.
- Warnings are used for suspicious but historically possible admin/user values.

Risks and edge cases:
- Some corrupt inodes cannot be loaded; repair must use the saved imap in `inode_repair.c`.
- Reflink nblocks can legitimately exceed physical block count.
- Realtime, metadir, and feature-gated formats require special validation paths.
