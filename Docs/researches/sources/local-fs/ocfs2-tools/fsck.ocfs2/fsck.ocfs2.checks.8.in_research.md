# File Research: sources/local-fs/ocfs2-tools/fsck.ocfs2/fsck.ocfs2.checks.8.in

Read coverage: complete file read, 1193 lines.

Purpose: manual page template documenting every fsck prompt code and the effect of answering yes.

Behavior and build role:
- The Makefile parses each `.SS "CODE"` heading to generate `prompt-codes.h`.
- Prompt call sites use these generated codes through `PR_<CODE>`.
- The document is both user documentation and a build-time registry of repair prompts.

Covered check families:
- Extent blocks/lists/records: block number, generation, depth/count/free fields, invalid extent blocks, out-of-range extents, unsupported unwritten/refcount flags, holes, overlaps, and CRC.
- Chain allocators and group descriptors: expected group positions, generations, parent/chain fields, loops, counts, free bits, discontiguous block groups, and global cluster count.
- Inodes/local allocators/truncate logs: inode allocator repair, generation mismatch, inode block location, root directory type, symlink consistency, directory zero blocks, inode size/clusters, inline data, sparse data, local allocators, and truncate records.
- Refcount trees: invalid flags/locations, refcount block fields, record ranges/collisions, empty/invalid blocks, cluster/file counts, redundant records, and refcount mismatch.
- Duplicate clusters: clone/delete/refcount-convert decisions for files and system files.
- Directory entries and connectivity: dot/dotdot rules, invalid names, inode ranges/free targets, file type mismatch, duplicate directory parents, duplicate filenames, record lengths, directory trailers, missing root/lost+found, disconnected directories/files, and link counts.
- Journals and cluster info: backup superblock recovery, missing orphan dirs, invalid or inconsistent journal files/features/sizes, dirty journal handling, and cluster-stack reconfiguration.
- Xattr/quota/directory index: invalid xattr blocks/entries/layout/hash/free accounting, quota block corruption choices, missing/corrupt directory indexes.

Risk notes:
- Prompt semantics explicitly say answering no leaves the filesystem unchanged, possibly causing later errors.
- Because prompt code generation depends on headings, changing this man page can affect compilation.
