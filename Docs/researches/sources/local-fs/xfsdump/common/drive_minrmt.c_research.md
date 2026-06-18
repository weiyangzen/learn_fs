# File Research: sources/local-fs/xfsdump/common/drive_minrmt.c

Purpose: drive strategy for non-SGI remote tape (`rmt`) devices. It is derived from the SCSI tape strategy and aims for media compatibility with the SCSI tape format.

Key constants and format:
- `STAPE_VERSION = 1`.
- `STAPE_MAGIC = 0x13579bdf02468ace`.
- `STAPE_HDR_SZ = PGSZ`; user data starts after the page-sized record/global-header area.
- Maximum record size is 2 MiB; minimum fallback max block size is 240 KiB.
- QIC mode uses 512-byte blocks.
- Ring length supports 1 to 10 buffers, default 3, but instantiation currently forces single-threaded operation.

Strategy selection:
- `ds_match` rejects `"stdio"`.
- The strategy only scores highly when the minimal-rmt option is present and a block size was specified.
- Opens the drive read-only during matching to confirm access.
- Warns that minimal rmt cannot be used without the block-size option.

Instantiation:
- Attaches `drive_ops`.
- Allocates `drive_context_t`.
- Forces `dc_singlethreadedpr = BOOL_TRUE`; ring-buffer code remains present but inactive.
- Parses options for ring length, ring pinning, record checksums, unload, QIC, overwrite, and media file size.
- Allocates a page-aligned 2 MiB record buffer for single-threaded operation.
- Initializes broad tape capabilities: BSF, FSF, rewind, files, next mark, read, removable, erase, eject.

Read path:
- `do_begin_read` prepares the drive if not already open, reads/validates the first media-file record, initializes offsets, and enters `OM_READ`.
- `do_read` returns available data from the current record, reading a new record via `getrec` as needed.
- `do_return_read_buf` reclaims caller-owned data and advances record state.
- `do_get_mark` exposes current media-file raw offset.
- `do_seek_mark` advances by consuming data, optionally using `MTFSR` when available.
- `do_next_mark` seeks to the next record mark and includes recovery logic for corruption, short reads, and QIC record-boundary hunting.
- `do_end_read` forward-spaces to the next file mark and leaves read mode.

Write path:
- `do_begin_write` requires the drive to already be open, fills the drive-specific record header, translates all nested media headers to on-media form, checksums the global header, writes the first header record, and initializes the next data record.
- `do_set_mark` records the current raw stream offset and stores the first mark offset in the record header.
- `do_get_write_buf` lends the caller a slice of the current record after the header area.
- `do_write` accepts the slice back, writes full records, initializes the next record header, and commits marks conservatively using `dc_lostrecmax`.
- `do_get_align_cnt` returns bytes to next page boundary.
- `do_end_write` pads/writes any partial final record, writes a tape file mark with `MTWEOF`, computes committed bytes, commits safe marks, discards remaining marks, and exits write mode.

Media positioning/control:
- `do_fsf`, `do_bsf`, `do_rewind`, `do_erase`, and `do_eject_media` wrap tape operations through `mt_op`.
- `do_erase` cannot rely on standard remote erase, so it writes a zeroed record beginning with `ERASE_MAGIC`.
- `do_get_device_class` always returns removable tape.
- `do_display_metrics` only reports ring metrics if the ring path is active.
- `do_quit` destroys any ring, closes the drive, and logs completion.

Validation and low-level I/O:
- `prepare_drive` opens the drive with retries, sets capabilities, chooses block/record sizes from the command line and QIC mode, handles overwrite, probes tape media, validates xfsdump headers, detects EFS dumps and xfsdump-erased tapes, and calculates end-of-media uncertainty.
- `validate_media_file_hdr` checks global header checksum, optional tape record checksum, translates nested headers, verifies global magic/version, drive strategy id, record magic, and record version.
- `record_hdr_validate` verifies optional checksum, record magic, non-null and matching dump UUID, record offset alignment, optional exact offset, and `rec_used` bounds.
- `read_record` maps short reads, blank/EOD, EIO, and other errors to `DRIVE_ERROR_*`.
- `write_record` optionally translates the record header, optionally sets record checksum, writes one full record, and maps failures through `determine_write_error`.
- `tape_rec_checksum_set/check` use two’s-complement sums over translated uint32_t words when record checksums are enabled.

Important interactions:
- Implements `drive_strategy_rmt`, referenced by `drive.c`.
- Uses `rmtopen`, `rmtclose`, `rmtioctl`, `rmtread`, and `rmtwrite` via macros that can switch to debug wrappers under `RMTDBG`.
- Uses `arch_xlate` for global/drive/media/content/content-inode/record header translation.
- Uses `cldmgr_stop_requested` during long prepare/probe loops.
- Shares media layout with `drive_scsitape.c` by design.

Risks/notes:
- `Open` treats `fd <= 0` as failure; if the process has stdin closed and `rmtopen` returns descriptor 0, this would be misclassified as failure.
- Ring-buffer code is substantial but currently disabled by forced single-threaded mode, increasing maintenance surface for inactive paths.
- RMT lacks several SCSI capability/status ioctls, so the code assumes capabilities and uses heuristic media probing.
- End-of-media commit accounting is conservative via `dc_lostrecmax` of 1 for QIC and 2 otherwise.
- The erase implementation is a marker write rather than physical media erase.
