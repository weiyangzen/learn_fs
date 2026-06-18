# File Research: sources/os/linux/linux-stable/fs/ocfs2/ocfs2_lockid.h

Purpose: defines OCFS2 cluster lock-id layout, lock type enum values, single-character lock type tags, and human-readable lock type names.

Read coverage: complete file read, 117 lines.

Key contents:
- Documents lock id strings as 32 bytes: one type byte, six reserved pad characters, 16 hex block-number characters, 8 hex generation characters, and NUL terminator.
- Defines `OCFS2_LOCK_ID_MAX_LEN`, `OCFS2_LOCK_ID_PAD`, and `OCFS2_DENTRY_LOCK_INO_START`.
- Enumerates lock types for metadata, data, super, rename, read/write, dentry, open, flock, quota info, NFS sync, orphan scan, refcount, and trim-fs locks.
- `ocfs2_lock_type_char()` maps lock types to DLM name prefixes such as `M`, `D`, `S`, `R`, `W`, `N`, `O`, `F`, `Q`, `Y`, `P`, `T`, and `I`.
- `ocfs2_lock_type_strings[]` and `ocfs2_lock_type_string()` provide debug-readable lock type names.

Dependencies:
- Used by DLM glue and debug paths that construct, parse, and report OCFS2 lock resources.

Risk and edge cases:
- Lock type chars and positions are protocol-visible through DLM lock names; changes can break compatibility between nodes.
- `ocfs2_lock_type_string()` only guards enum range with `BUG_ON()` under `__KERNEL__`; non-kernel consumers must pass valid enum values.
