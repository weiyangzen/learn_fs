# File Research: sources/os/linux/linux-stable/fs/ocfs2/dlmglue.h

Purpose: Declares OCFS2 DLM glue data formats, lock flags, locking subclasses, and public lock-management APIs.

Read coverage: complete file read, 207 lines.

Key contents:
- LVB ABI structures for inode metadata, quota info, orphan scan sequence, and trimfs state.
- `struct ocfs2_trim_fs_info` as the CPU-endian trimfs handoff format.
- `struct ocfs2_lock_holder` used by recursive-lock tracking.
- Metadata lock argument flags: recovery wait suppression, noqueue, nonblocking, and get-buffer-only behavior.
- Inode cluster-lock subclasses for normal, parent, rename ordering, and reflink target contexts.
- Public prototypes for DLM lifecycle, lock-resource initialization/freeing, inode/RW/open/dentry/file/quota/refcount/global locks, and downconvert wakeup.
- Convenience macros for common inode-lock variants.

Important invariants:
- LVB versions are explicit ABI checks between mounted nodes.
- Tracker variants distinguish first lock acquisition from recursive compatible lock use and forbid PR-to-EX recursive upgrades.
- `OCFS2_META_LOCK_GETBH` means the caller already has cluster-lock coverage and only wants an up-to-date dinode buffer.

Dependencies:
- Includes `dcache.h` for dentry-lock types and depends on OCFS2 superblock, inode, quota, refcount, folio, and buffer-head declarations from surrounding headers.

Risk notes:
- Any LVB layout or version change affects cluster interoperability.
- Lock flag semantics are tightly coupled to `dlmglue.c`; adding a flag requires auditing wait and downconvert paths.
