# File Research: sources/local-fs/xfsdump/common/drive_scsitape.c

## Summary
Implements the `drive_strategy_scsitape` backend for SCSI tape, remote tape, TS/TMF tape drivers, and QIC-style fixed-block devices. It adapts xfsdump/xfsrestore’s generic `drive_ops_t` interface to Linux tape ioctls, remote tape protocol calls, record framing, media-file labels, file marks, and tape positioning.

## Main Responsibilities
- Matches tape devices by remote path syntax or character-device major number.
- Opens, prepares, sizes, reads, writes, rewinds, spaces, erases, and optionally unloads tape media.
- Encodes each tape media file as fixed-size tape records with an xfsdump global header in the first record and `rec_hdr_t` metadata in every record.
- Negotiates fixed or variable block size, command-line block size, QIC constraints, and Linux/TS driver quirks.
- Implements media marks as byte offsets into the framed tape stream and supports forward mark search/resynchronization.
- Converts global/media/content/record headers through `arch_xlate` so media format remains endian-aware.
- Tracks uncertainty after end-of-media write errors and commits or discards queued marks accordingly.

## Core State
`drive_context_t` stores operational mode, ring/buffer ownership, current record pointers, record and I/O counters, tape fd, remote/variable/QIC/capability flags, selected block and record size, lost-record margin, checksum mode, unload/overwrite flags, and requested media file size.

The file currently forces `dc_singlethreadedpr = BOOL_TRUE`, but retains full ring-buffer support through `ring_read()`, `ring_write()`, and `Ring_*()` wrappers.

## Important Behavior
`ds_match()` rejects `stdio`, gives remote `host:path` devices a high match only if `MTIOCGET` succeeds, and detects local tape devices by comparing character major numbers for `st`, `ts`, and `tmf`.

`do_begin_read()` allocates or acquires a record buffer, calls `prepare_drive()` on first open, reads and validates the media label, initializes read offsets, and enters `OM_READ`.

`prepare_drive()` is the central tape probing path. It retries open/status while the drive becomes ready, rejects write-protected media during dump, detects variable block mode, queries tape capabilities, handles `--overwrite`, chooses initial record/block sizes, disambiguates file-mark position, and loops through read/status outcomes to classify blank, foreign, corrupt, EOD, EOM, wrong block size, and valid xfsdump media.

`validate_media_file_hdr()` verifies the global header checksum, optional tape record checksum, xfsdump magic/version, drive strategy id, SCSI tape magic/version, and then converts the first record into native header structures.

`do_read()`, `do_return_read_buf()`, `getrec()`, and `read_record()` expose only payload bytes after `STAPE_HDR_SZ`, while maintaining record counters and detecting EOF/EOD/EOM/corruption from read size plus tape status.

`do_seek_mark()` treats marks as raw media-file offsets and advances only forward, using buffered reads, optional `MTFSR`, and dummy reads to reach a requested mark.

`do_next_mark()` finds the next record-level mark or, after corruption/read error, tries to resynchronize by reading records, validating headers, optionally hunting QIC 512-byte block boundaries, and forward-spacing past bad tape blocks.

`do_begin_write()` writes the media-file header record, initializes the next data record header, and enters write mode. `do_write()` writes full records, prepares the next record header, and commits marks only after subtracting `dc_lostrecmax`. `do_end_write()` writes the padded final record if needed, flushes pending ring writes, writes a tape file mark, computes committed bytes, commits/discards marks, and exits write mode.

Tape movement helpers (`do_fsf()`, `do_bsf()`, `rewind_and_verify()`, `fsf_and_verify()`, `bsf_and_verify()`) wrap Linux tape ioctls and include driver-specific status workarounds. `map_ts_status()` maps TS/SGI tape status bits into Linux `mtget.mt_gstat` style bits.

## Dependencies
Depends on xfsdump drive/media/global/content headers, `ring`, `rec_hdr`, `arch_xlate`, `ts_mtio`, logging/dialog/control helpers, remote tape functions, Linux tape ioctls, `/proc/devices`, and UUID APIs.

## Risks
Tape status semantics are highly driver-specific; much of the correctness depends on Linux ST versus TS behavior, especially EOF/EOD/EOT and file-mark positioning.

The block-size detection loop is heuristic and can classify media as blank, foreign, corrupt, or wrong-sized based on subtle combinations of `read()` length, `errno`, and tape status.

Remote tape lacks capability and block-size ioctls, so the code falls back to conservative assumptions.

Record checksum use is optional and only checked when the on-media header says a checksum is present and checksum mode is enabled.

`do_quit()` unloads when requested but does not visibly close/free all context resources in the same way `drive_simple` does; lifecycle appears owned by broader drive shutdown assumptions.

The file contains old TS/APD and Linux ST workaround logic that is hard to validate without real tape hardware.
