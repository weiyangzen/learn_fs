# File Research: sources/local-fs/jfsutils/libfs/logredo.h

This header defines logredo return codes, replay constants, workspace structures, and public replay APIs.

Contents:
- Error severity notes: positive return codes make fsck continue with full repair; negative return codes also request log reformat.
- Many specific error codes for memory failures, bmap/imap I/O, superblock I/O, journal parsing, bad log versions, invalid log addresses, page update ranges, and unsupported log states.
- Error-type constants used by `fsError()` and `logError()`.
- `PB_READ` and `PB_UPDATE` operation constants.
- `INLINELOG` and `OUTLINELOG` location bits.
- `NBUFPOOL` buffer-cache size.
- `struct dmap_bitmaps`, `struct bmap_wsp`, `struct iag_data`, and `struct imap_wsp`, which hold per-replay working and persistent allocation-map state.
- `struct log_info Log`, describing journal file, serial, location, byte offset, size, block size, UUID, and device number.
- `struct vopen`, the per-active-volume state used across logredo, including open file handle, UUID, superblock-derived geometry, imap workspaces, and bmap workspaces.
- Public prototypes `jfs_logredo()` and `findLog()`.

Integration points:
- Included by `logredo.c`, `log_read.c`, and `log_work.c`.
- Depends on JFS map and inode structures from other headers.

Notes:
- `#define fsimap_iag fsimap_lst.fsimapiag` appears stale or incorrect because `struct fsimap_lst` has no `fsimapiag` member in this header.
- The error-code sign convention is critical for callers: negative means reformat log, positive means run full fsck without necessarily reformatting.
