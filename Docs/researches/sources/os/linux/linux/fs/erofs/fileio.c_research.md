# File Research: sources/os/linux/linux/fs/erofs/fileio.c

Implements EROFS file-backed image I/O.

Key behavior:
- Defines request objects embedding a bio, fixed bvec array, kiocb, superblock, and refcount.
- Submits reads to the backing file with `vfs_iocb_iter_read()`, optionally using direct I/O when mount option and file mode allow it.
- Completion validates full-length reads, propagates errors to bios or online folios, ends bios, and frees request state.
- Provides bio allocation/submission wrappers for code that issues block-like reads against file-backed devices.
- `erofs_fileio_scan_folio()` maps each folio range, copies inline metadata, zeroes holes, or batches mapped extents into file-backed bio-style reads.
- Splits online folio completion for each attached async segment.
- Implements read_folio and readahead aops for file-backed mode.

Important interactions:
- Uses `erofs_map_blocks()` and `erofs_map_dev()` to translate logical file data to backing-file offsets.
- Cooperates with online folio helpers in `data.c`.
- Selected by `erofs_get_aops()` when `CONFIG_EROFS_FS_BACKED_BY_FILE` and file-backed mode are active.
