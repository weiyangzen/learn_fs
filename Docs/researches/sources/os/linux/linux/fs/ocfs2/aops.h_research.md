# File Research: sources/os/linux/linux/fs/ocfs2/aops.h

Header for OCFS2 address-space operation helpers shared with other OCFS2 files.

Key declarations:
- `ocfs2_map_folio_blocks()`, `ocfs2_unlock_and_free_folios()`, `walk_page_buffers()`.
- `ocfs2_write_begin_nolock()` / `ocfs2_write_end_nolock()` for nonstandard write flows such as mmap and direct I/O.
- `ocfs2_read_inline_data()`, `ocfs2_size_fits_inline_data()`, and `ocfs2_get_block()`.
- `ocfs2_write_type_t` distinguishes buffered, direct, and mmap write callers.

Direct-I/O lock state:
- Defines bit helpers storing OCFS2 rw-lock state in `kiocb->private`.
- `OCFS2_IOCB_RW_LOCK` tracks whether a lock is held.
- `OCFS2_IOCB_RW_LOCK_LEVEL` stores lock level.
- These helpers are paired with `ocfs2_dio_end_io()` in `aops.c` and file read/write paths.

Notable issue:
- The include guard closes with comment `OCFS2_FILE_H`, while the guard name is `OCFS2_AOPS_H`; cosmetic only.
