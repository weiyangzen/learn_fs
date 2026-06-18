# File Research: sources/os/linux/linux-stable/fs/ocfs2/file.h

Purpose: Declares OCFS2 file/directory operation tables, per-file private state, and file-size/allocation helper APIs.

Read coverage: complete file read, 74 lines.

Key contents:
- Extern declarations for file and inode operation tables, including no-posix-cluster-lock variants.
- `struct ocfs2_file_private` stores a directory seek cookie, owning `struct file`, mutex, and flock lock resource.
- Prototypes for allocation extension, inode size update, truncation, no-hole extension, zero extension, setattr/getattr/permission, atime handling, file-space reservation/punching, refcount-range checking, and inode-range removal.

Important invariants:
- File-private state owns an OCFS2 lock resource that must be initialized on open and dropped/freed on release.
- Allocation helpers assume higher-level callers have acquired appropriate inode, cluster, journal, and allocation locks.

Dependencies:
- Tied to `file.c`, `dlmglue.c`, allocation contexts, buffer heads, quota/refcount logic, and VFS operation tables.

Risk notes:
- Public helper prototypes expose low-level mutation routines whose correctness depends on caller-side lock and transaction discipline.
