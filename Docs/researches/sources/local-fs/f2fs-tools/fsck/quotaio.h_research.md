# File Research: sources/local-fs/f2fs-tools/fsck/quotaio.h

Purpose: public interface and shared data model for quota IO and in-memory quota accounting.

Key contents:
- Defines quota types `USRQUOTA`, `GRPQUOTA`, `PRJQUOTA`, and bit masks.
- Defines quota size-check modes used while validating quota file sizes.
- Declares global quota size-check state arrays.
- Defines `quota_ctx`, which holds the F2FS superblock info, per-type quota dictionaries, open quota file handles, and linked-inode tracking.
- Defines quota format IDs, default grace periods, and `IOFL_INFODIRTY`.
- Defines `quota_file`, `quota_handle`, `util_dqinfo`, `util_dqblk`, `dquot`, and `quotafile_ops`.
- Declares quota file lifecycle APIs, dquot allocation, grace update, quota context lifecycle, accounting helpers, quota writing, and compare/update.
- Provides small allocation wrappers `quota_get_mem()`, `quota_get_memzero()`, and `quota_free_mem()`.

Important dependencies:
- Includes `dict.h`, F2FS headers, `node.h`, `fsck.h`, and `dqblk_v2.h`.
- Used by all quota implementation files and by fsck quota checks.

Risk notes:
- `quota_free_mem()` nulls the caller’s pointer by memcpy into an opaque pointer location; callers must pass the address of a pointer.
- The comment still references ext4 superblock fields in the ported header, but current usage is F2FS quota inode based.
