# File Research: sources/os/linux/linux-stable/fs/ocfs2/aops.h

## Summary
Declares the shared OCFS2 address-space helper API used by file, mmap, and direct-I/O paths, plus the small `kiocb->private` bit protocol used to release OCFS2 rw locks from direct-I/O completion.

## Main Responsibilities
- Expose folio block mapping and folio cleanup helpers.
- Expose the nolock write begin/end core and its caller type enum.
- Expose inline-data read/size helpers and generic `ocfs2_get_block()`.
- Define helper macros for tracking whether a direct-I/O `kiocb` owns an OCFS2 rw lock and at which level.

## Key Interfaces
- `ocfs2_write_type_t` distinguishes buffered, direct, and mmap writes.
- `ocfs2_write_begin_nolock()` and `ocfs2_write_end_nolock()` are the core reusable write lifecycle.
- `ocfs2_iocb_set_rw_locked()`, `ocfs2_iocb_clear_rw_locked()`, and `ocfs2_iocb_rw_locked_level()` encode DIO lock ownership in `iocb->private`.

## Risks
The `kiocb->private` bit use is compact but fragile: all participants must treat the pointer storage as bit flags while DIO is in progress, and completion must clear and unlock exactly once.
