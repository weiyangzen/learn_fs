# File Research: sources/os/bsd/netbsd-src/sys/ufs/ufs/ufs_wapbl.h

This header defines UFS integration points for WAPBL journaling. It contains superblock journal constants and macros that compile to real journaling operations when WAPBL is enabled or no-ops otherwise.

Key responsibilities:
- Define journal metadata values stored in UFS superblocks.
- Describe supported journal allocation locations.
- Define journal creation/clear flags and journal size bounds.
- Wrap WAPBL begin/end/update/assert/register operations behind UFS macros.
- Provide no-op fallbacks when WAPBL support is not compiled in.

Important constants:
- `UFS_WAPBL_VERSION`: Journal metadata version.
- `UFS_WAPBL_JOURNALLOC_NONE`: No journal.
- `UFS_WAPBL_JOURNALLOC_END_PARTITION`: Journal at end of partition, with locator slots for address/count/block size.
- `UFS_WAPBL_JOURNALLOC_IN_FILESYSTEM`: Journal inside filesystem, with locator slots for address/count/block size/inode.
- `UFS_WAPBL_FLAGS_CREATE_LOG` and `UFS_WAPBL_FLAGS_CLEAR_LOG`: Superblock journal action flags.
- `UFS_WAPBL_JOURNAL_SCALE`, `MIN`, `MAX`: Default and bounded journal sizing.

Important macros/functions:
- `ufs_wapbl_begin` / `ufs_wapbl_end`: Inline wrappers around `wapbl_begin` and `wapbl_end` if the mount has a journal.
- `UFS_WAPBL_BEGIN` / `UFS_WAPBL_END`: Standard transaction wrappers used throughout UFS code.
- `UFS_WAPBL_UPDATE`: Calls `UFS_UPDATE` only when journaling is present.
- `UFS_WAPBL_JLOCK_ASSERT` / `JUNLOCK_ASSERT`: Diagnostic lock-state assertions.
- `UFS_WAPBL_REGISTER_INODE`, `UNREGISTER_INODE`, `REGISTER_DEALLOCATION`, `UNREGISTER_DEALLOCATION`: Journal registration hooks for inode and block deallocation tracking.

Important interactions:
- Included by lookup, rename, read/write, quota2, and vnode operations.
- Bridges generic UFS code and the kernel WAPBL subsystem without forcing all builds to include WAPBL behavior.

Notable behavior:
- Without WAPBL, transaction begin always returns 0 and update/register macros are no-ops or return 0.
- A comment questions whether the 64 MB journal maximum is too restrictive.
