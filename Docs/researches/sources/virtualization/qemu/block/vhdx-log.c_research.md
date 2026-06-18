# File Research: sources/virtualization/qemu/block/vhdx-log.c

`vhdx-log.c` implements VHDX metadata log parsing, validation, replay, writing, and immediate flushing. The VHDX log is a circular buffer of 4 KiB sectors located at the offset/length from the active VHDX header. It journals metadata changes such as BAT entry updates so a dirty image can be recovered on open.

Internal helper structs are `VHDXLogSequence`, representing a contiguous valid sequence of log entries, and `VHDXLogDescEntries`, a log entry header followed by flexible-array descriptors. `zero_guid` marks an empty log. Indexing uses `vhdx_log_inc_idx()` to advance one 4 KiB sector with wraparound.

Read-side primitives include `vhdx_log_peek_hdr()`, which reads but does not advance the current header; `vhdx_log_read_sectors()`, which reads sectors from the circular log and optionally advances `read`; and `vhdx_log_reset()`, which clears read/write pointers and updates headers with a zero log GUID. `vhdx_log_write_sectors()` writes sectors to the circular log, after calling `vhdx_user_visible_write()`, and stops before colliding with the read pointer.

Validation checks are layered. `vhdx_log_hdr_is_valid()` verifies signature, entry length bounds/alignment, nonzero sequence number, matching active header log GUID, and descriptor-count bounds. `vhdx_log_desc_is_valid()` checks descriptor sequence, 4 KiB file-offset alignment, and valid `zero` or `desc` signatures; zero descriptors must have 4 KiB-aligned lengths. `vhdx_log_read_desc()` reads descriptor sectors, converts descriptors to host order when requested, and validates each descriptor. `vhdx_validate_log_entry()` verifies a full entry, sequence continuity, descriptor validity, data sector reads, and CRC32C across descriptor and data sectors.

Replay uses `vhdx_log_search()` to scan the circular buffer for the highest-sequence valid active log sequence. `vhdx_parse_log()` initializes log offset/length from the active header, rejects bad log offsets/version/length, exits if GUID or length says no log is present, searches for a valid sequence, refuses read-only open if replay is required, and otherwise flushes the sequence into the image. The read-only failure message points users to `qemu-img check -r all`.

`vhdx_log_flush()` replays a validated sequence. For each entry it re-peeks the header, rejects logs whose flushed-file offset exceeds current file length, reads descriptors, reads data sectors for data descriptors, converts data sector endian fields, applies each descriptor via `vhdx_log_flush_desc()`, extends the file to `last_file_offset` rounded to MiB if needed, flushes the block node, and resets the log. `vhdx_log_flush_desc()` reconstructs full 4 KiB data sectors from descriptor leading/trailing bytes plus the data-sector payload, or writes explicit zero sectors for zero descriptors.

Write-side logging is intentionally simple: `vhdx_log_write_and_flush()` flushes existing data, calls `vhdx_log_write()`, flushes the log, then immediately replays the just-written log. `vhdx_log_write()` creates a new log GUID if the header currently has zero log GUID; otherwise it returns `-ENOTSUP` because this implementation requires flushing after every write. It computes sector coverage for possibly unaligned writes, merges partial leading/trailing sectors with existing file contents, builds descriptors and data sectors in little-endian form through `vhdx_log_raw_to_le_sector()`, computes the entry checksum, writes all sectors to the circular log, increments sequence, and updates tail.

Important risks and invariants:
- Log writes are immediately flushed, simplifying consistency but limiting batching.
- Read-only open refuses dirty logs because replay must modify the image.
- Partial-sector journal writes depend on reading destination file contents before logging.
- `flushed_file_offset` protects against replaying a log into a truncated image.
- All checksum and endian handling must occur on the correct disk-order buffers.
