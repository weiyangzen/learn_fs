# File Research: sources/os/linux/linux/fs/ocfs2/ocfs2_lockid.h

Role: Defines the OCFS2 DLM lock-name format and lock type identifiers.

Key contents:
- Lock ID layout:
  - byte 0: lock type character
  - bytes 1-6: reserved pad `"000000"`
  - bytes 7-22: block number as 16 hex characters
  - bytes 23-30: inode generation as 8 hex characters
  - byte 31: NUL
- `OCFS2_LOCK_ID_MAX_LEN` is 32.
- `OCFS2_DENTRY_LOCK_INO_START` marks the inode-number start offset for dentry lock names.
- `enum ocfs2_lock_type` covers metadata, data, super, rename, read/write, dentry, open, flock, quota info, NFS sync, orphan scan, refcount, trimfs, and count.
- `ocfs2_lock_type_char()` maps lock types to single-character DLM name prefixes:
  - meta `M`, data `D`, super `S`, rename `R`, rw `W`, dentry `N`, open `O`, flock `F`, quota `Q`, NFS sync `Y`, orphan scan `P`, refcount `T`, trimfs `I`
- `ocfs2_lock_type_strings[]` maps lock types to human-readable debug strings.
- `ocfs2_lock_type_string()` returns the debug string and asserts valid types under `__KERNEL__`.

Design notes:
- The compact lock name encodes enough object identity for cluster-wide DLM coordination and debugging.
- Read/write uses `W` because `R` is already used by rename.
