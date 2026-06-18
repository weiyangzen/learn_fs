# File Research: sources/os/linux/linux/fs/ocfs2/filecheck.h

Header for OCFS2 online file check.

Defines:
- Filecheck status codes:
  - success
  - failed
  - in progress
  - read-only
  - in journal
  - invalid inode
  - block ECC
  - block number
  - valid-flag
  - generation
  - unsupported
- Error range macros: `OCFS2_FILECHECK_ERR_START` and `OCFS2_FILECHECK_ERR_END`.
- `struct ocfs2_filecheck`: list head, spinlock, max entry count, current entry count, finished entry count.
- Queue bounds: min 10, max 100.
- Operation types: check, fix, and set-max.
- `struct ocfs2_filecheck_sysfs_entry`: sysfs kobject, unregister completion, and pointer to filecheck state.

Exports:
- `ocfs2_filecheck_create_sysfs()`
- `ocfs2_filecheck_remove_sysfs()`

Role:
- Provides the mount-level sysfs state structure embedded in `struct ocfs2_super` and the create/remove hooks called by mount lifecycle code.
