# File Research: sources/local-fs/xfsdump/common/drive_simple.c

## Summary
Implements `drive_strategy_simple`, the backend for dump/restore streams stored in ordinary files, stdio, FIFOs, raw/block devices, and remote ordinary files through the rmt protocol. It supports exactly one media file and uses a simple page-aligned memory buffer instead of tape record framing.

## Main Responsibilities
- Matches fallback non-directory paths, `stdio`, and weakly matches remote `host:path` names.
- Opens stdio, local files/devices/FIFOs, or remote files with dump/restore-appropriate flags.
- Reads and writes the xfsdump global/media/content header.
- Buffers stream I/O in a 64-page page-aligned buffer.
- Maintains simple byte-offset marks for restore positioning.
- Supports rewind and erase when the backing object is seekable/truncatable.

## Important Behavior
`ds_instantiate()` allocates a page-aligned `drive_context_t`, records whether the path is remote, opens the path, and sets capabilities based on build mode and file type. Regular files can read, rewind, and erase; FIFOs generally cannot rewind; stdio maps to fd 1 for dump and fd 0 for restore.

`do_begin_read()` allows only one media file, initializes the read buffer, reads `GLOBAL_HDR_SZ` through the drive read callbacks, verifies the global checksum, translates headers, checks magic/version/strategy id, stores the first mark from `dh_specific`, and enables `DRIVE_CAP_NEXTMARK` if that mark exists.

`do_read()` refills the buffer with `read()` when empty and returns slices to the caller. Zero bytes from the backing fd maps to `DRIVE_ERROR_EOD`.

`do_seek_mark()` only seeks forward by consuming bytes through `read_buf()`. `do_next_mark()` only knows the first mark recorded in the media header.

`do_begin_write()` truncates readable destinations, initializes write buffering, writes a translated/checksummed global header through `write_buf()`, and records no first mark initially.

`do_set_mark()` records each mark offset. For the first mark, it either patches the still-buffered header or, for random-access outputs, seeks back to rewrite the on-media header and checksum. If the mark is already committed it calls the callback immediately; otherwise it queues the mark.

`do_write()` accepts ownership of a buffer slice and flushes the full buffer when filled, committing marks up to the flushed offset. `do_end_write()` flushes remaining bytes, rounds raw device output to `BBSIZE`, commits marks, bumps the single file-mark count, and reports committed bytes.

`do_rewind()` seeks to offset zero. `do_erase()` seeks to zero and truncates to zero length.

## Dependencies
Depends on xfsdump drive/global/media/content structures, `util` buffered I/O helpers, `arch_xlate`, rmt operations, logging, and build-time `DUMP`/`RESTORE` modes.

## Risks
The strategy intentionally supports only one media file; after one successful read or write, later begin operations return EOM.

First-mark persistence depends on either the mark being set before the initial buffer flush or the destination being randomly seekable.

Short writes on full-buffer flush map to EOM after committing only the bytes written; callers rely on mark commit/discard behavior to stay consistent.

The rmt macro remapping makes ordinary file access go through remote-tape wrappers, which can hide normal POSIX behavior behind rmt semantics.
