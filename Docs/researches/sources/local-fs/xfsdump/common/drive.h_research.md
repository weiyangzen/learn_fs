# File Research: sources/local-fs/xfsdump/common/drive.h

Purpose: central drive abstraction contract for xfsdump/xfsrestore media I/O.

Key structures:
- `drive_hdr_t`: drive-layer on-media header embedded in `global_hdr_t.gh_upper`.
- `drive_strategy_t`: match/instantiate strategy object with recommended mark separation and media-file size.
- `drive_mark_t` and `drive_markrec_t`: mark tokens and callback records for committed-write tracking.
- `drive_t`: instantiated drive manager with strategy, ops, contexts, read/write headers, pathname, capabilities, estimates, and mark queue.
- `drive_ops_t`: full media operation table.

Key operation categories:
- Lifecycle: `do_init`, `do_sync`, `do_quit`.
- Read flow: `do_begin_read`, `do_read`, `do_return_read_buf`, `do_get_mark`, `do_seek_mark`, `do_next_mark`, `do_end_read`.
- Write flow: `do_begin_write`, `do_set_mark`, `do_get_write_buf`, `do_write`, `do_get_align_cnt`, `do_end_write`.
- Position/media control: `do_fsf`, `do_bsf`, `do_rewind`, `do_erase`, `do_eject_media`.
- Metadata/metrics: `do_get_device_class`, `do_display_metrics`.

Important semantics:
- Media I/O is scoped to media files.
- Marks are callbacks for determining what data is safely committed, especially near end-of-media.
- Reads may encounter duplicated data across media boundaries because writes after the last committed mark may or may not have reached media.
- `end_read`/`end_write` virtually position the drive at the next media file.
- Buffer ownership is explicit: callers must return read buffers and must commit write buffers before requesting another.

Capabilities and errors:
- Capabilities include back/forward spacing, rewind, multiple files, append/overwrite/erase, next-mark seek, eject, autorewind, read, and removable media.
- Error codes cover corruption, EOF/EOD/EOM/BOM, device, format, media, version, core, timeout, stop, invalid, blank, foreign, and overwrite.

Risks/notes:
- `DRIVE_CAP_OVERWRITE` and `DRIVE_CAP_ERASE` both use `(1 << 6)`, so erase and overwrite are indistinguishable at the bitmask level.
- The interface is intentionally low-level and stateful; callers must follow begin/read-or-write/end sequencing exactly.
