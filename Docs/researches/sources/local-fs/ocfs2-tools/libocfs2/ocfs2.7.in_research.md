# File Research: sources/local-fs/ocfs2-tools/libocfs2/ocfs2.7.in

Manual page documenting OCFS2 filesystem semantics, features, tools, cluster stack behavior, operational notes, and debugging guidance.

Core positioning:
- OCFS2 is described as a POSIX-compliant shared-disk cluster filesystem for Linux with local-filesystem semantics across nodes.
- It promises cluster-wide cache coherency across buffered, direct, async, splice, and mmap IO.
- It uses journaling; surviving nodes replay journals of dead nodes.
- It is architecture and endian neutral, matching the byte-swap support in libocfs2 files.

Feature overview:
- Tunable block sizes: 512, 1K, 2K, 4K, with 4K generally recommended.
- Tunable cluster sizes: 4K through 1M.
- Multiple cluster stacks: `o2cb`, userspace stacks `pcmk`/`cman`, and no-stack local mount.
- Extent allocations, sparse files, unwritten extents, hole punching, inline data, reflink/refcount, allocation reservation, indexed directories, file attributes, xattrs, metadata checksums, ACL/security xattrs, quotas, clustered flock/fcntl, online resize, and tool support.

Compatibility model:
- Explains compat, incompat, and ro-compat feature flags.
- Lists feature bits and associated kernel/tool versions, including `indexed-dirs`, `metaecc`, `refcount`, `discontig-bg`, `usrquota`, and `grpquota`.
- Documents how unsupported incompat and ro-compat features surface in mount errors.

Operational guidance:
- Covers formatting and converting local mounts, O2CB local/global heartbeat, and userspace cluster stack updates.
- Lists major filesystem utilities: `mkfs.ocfs2`, `tunefs.ocfs2`, `fsck.ocfs2`, `mount.ocfs2`, `o2cluster`, `o2info`, `debugfs.ocfs2`, `o2image`, and `mounted.ocfs2`.
- Lists O2CB tools: `o2cb`, `ocfs2_hb_ctl`, and `o2hbmonitor`.

Filesystem notes:
- Explains delayed deletion through link count, cluster-wide open references, orphan directories, truncate logs, and sync.
- Explains why directory listing can be expensive in clustered filesystems due to inode stat locking.
- Describes allocation reservation behavior and reflink disk-usage reporting, including need for shared-extent-aware tools.
- Documents discontiguous block groups, backup superblock locations, synthetic filesystems (`configfs`, `dlmfs`, `debugfs`), DLM debugging workflow, NFS export limitations, filesystem size limits, system object layout, heartbeat/quorum/fencing, and kernel thread roles.

Relevance to code group:
- Documents features implemented or supported by adjacent files: endian neutrality (`inode.c`, `quota.c`, `refcount.c`), metadata ECC (`inode.c`, `quota.c`, `openfs.c`, `refcount.c`), indexed directories (`lookup.c`, `link.c`), quotas (`quota.c`), reflink/refcount (`refcount.c`), discontiguous block groups (`inode_scan.c`), lock debugging (`lockid.c`), journals (`mkjournal.c`), and backup superblocks/opening (`openfs.c`).
