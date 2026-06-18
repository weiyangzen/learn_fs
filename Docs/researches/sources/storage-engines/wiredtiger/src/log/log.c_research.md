# sources/storage-engines/wiredtiger/src/log/log.c

## Purpose
`log.c` is the physical transaction-log implementation for WiredTiger. It creates, opens, verifies, writes, scans, truncates, salvages, syncs, and removes numbered `WiredTigerLog.NNNNNNNNNN` files. It sits below transaction logging (`src/txn/txn_log.c`) and log manager lifecycle (`log_mgr.c`), and above the filesystem, compression, encryption, checksum, capacity throttling, and recovery subsystems.

The file turns caller-built `WT_LOG_RECORD` buffers into durable on-disk records with aligned padding, little-endian headers, checksums, optional compression/encryption, and LSN allocation through group-commit slots. It also implements the defensive scanner used by recovery, log cursors, printlog, and recovery probes.

## Important APIs and Functions
- `__wt_log_printf` / `__wt_log_vprintf`: build `WT_LOGREC_MESSAGE` records for internal diagnostic/system messages and write them through normal logging.
- `__wt_log_write`: public write entry point. Applies optional log compression and connection-level encryption, then delegates to `__log_write_internal`.
- `__log_write_internal`: fills the log record header, rounds to `WTI_LOG_ALIGN`, computes checksum, joins a `WTI_LOGSLOT`, writes/copies data, releases the slot, and waits for `WT_LOG_FLUSH` or `WT_LOG_FSYNC` guarantees when requested.
- `__wt_log_scan`: reads log files record by record, verifies headers and checksums, handles compression/encryption, detects holes/partial writes, invokes a caller callback, and truncates during recovery/salvage.
- `__wt_log_flush`, `__wt_log_flush_lsn`, `__wt_log_force_sync`: force buffered records out to OS or disk and return/advance write and sync LSNs.
- `__wt_log_get_backup_files`: computes log files needed for backup from allocation and checkpoint LSNs, forces a file switch, and filters directory listings.
- `__wt_log_needs_recovery`: opens a log cursor at checkpoint LSN and decides whether commit records exist after the checkpoint.
- `__wti_log_open`, `__wti_log_close`: open current/new log files at connection startup and close file handles at shutdown.
- `__wti_log_acquire`, `__wti_log_release`, `__wti_log_force_write`, `__wti_log_fill`: slot allocation/write/release primitives used by group commit and manager threads.
- `__wti_log_allocfile`, `__wti_log_remove`, `__wt_log_filename`, `__wti_log_extract_lognum`: file naming and filesystem operations for real, temporary, and preallocated log files.
- `__wti_log_set_version`, `__wt_log_compat_verify`: enforce compatibility-version log formats.

## Control Flow
Write path:
1. Caller passes a prebuilt `WT_LOG_RECORD` in a `WT_ITEM` to `__wt_log_write`.
2. The record may be compressed if the configured compressor produces a smaller aligned record, then encrypted if a keyed encryptor exists.
3. `__log_write_internal` pads to `WTI_LOG_ALIGN`, writes `len/checksum/flags/mem_len`, and computes the checksum over little-endian header bytes.
4. The writer joins the active slot with `__wti_log_slot_join`. Oversized, forced, or boundary-crossing records trigger `__wti_log_slot_switch`.
5. `__wti_log_fill` copies to the slot buffer or writes directly for forced/unbuffered records.
6. `__wti_log_slot_release` accounts for copied bytes. If the slot is done, `__wti_log_release` writes buffered bytes and either hands the slot to the write-LSN server or synchronously advances `write_lsn`/`sync_lsn`.

Read/recovery path:
1. `__wt_log_scan` derives `start_lsn` and `end_lsn` from explicit input, `WT_LOGSCAN_FIRST`, `WT_LOGSCAN_FROM_CKP`, or existing files when logging is disabled.
2. It opens/verifies the starting file with `__log_open_verify`, including descriptor magic/version and optional previous-LSN system record.
3. It reads at least one alignment unit, expands to the rounded record length, checks for zero-filled preallocation, holes, oversize lengths, checksum mismatches, partial writes, and backup-specific artifacts.
4. Valid records are byte-swapped, decrypted, decompressed, and passed to the callback unless they are file headers.
5. Recovery scans truncate at the discovered end and may salvage by truncating damaged logs when `WT_CONN_SALVAGE` is set.

File rollover path:
1. `__wti_log_acquire` checks whether the next allocation fits the current file or a forced new file flag is set.
2. `__log_newfile` waits for any prior file handle pending close, publishes `log_close_lsn/log_close_fh`, increments `fileid`, uses a preallocated file if available and safe, otherwise allocates a temporary file and renames it.
3. The new file receives a descriptor header and, for modern log versions, a system record containing the previous LSN.

## State and Persistence Behavior
- Persistent files are numbered log files under `log_mgr.log_path`, using `WT_LOG_FILENAME`, plus temporary/preallocated files using `WTI_LOG_TMPNAME` and `WTI_LOG_PREPNAME`.
- Each file begins with a fixed aligned descriptor containing magic, log version, and configured max file size.
- For `WTI_LOG_VERSION_SYSTEM` and later, the first real record stores the previous LSN so recovery can detect holes across file boundaries.
- `alloc_lsn` reserves future byte ranges, `write_lsn` tracks records written to the OS, `write_start_lsn` tracks the start of the last written record, `sync_lsn` tracks fsynced durability, `sync_dir_lsn` tracks parent-directory durability, and `trunc_lsn` records recovery truncation bounds.
- Log files are preallocated/zero-filled, so scanner logic treats zeroed ranges as EOF only after proving no later non-zero data exists.
- Truncation prefers filesystem truncate but falls back to zero-filling when truncate is unsupported or unsafe during backup.
- Compression and encryption flags are persisted in `WT_LOG_RECORD.flags`; `mem_len` persists uncompressed size for compressed/encrypted payload handling.

## Dependencies and Integration Points
- Uses `log_private.h` slot state, file prefixes, and private prototypes; uses public declarations and LSN macros from `log.h`.
- Consumed by transaction commit/checkpoint code (`__wti_txn_log_commit`, `__wt_checkpoint_log`) and log cursor/printlog paths.
- Coordinates with `log_mgr.c` background threads via `log_mgr.file.cond`, `log_mgr.server.cond`, and `log_mgr.wrlsn.cond`.
- Depends on filesystem wrappers (`__wt_open`, `__wt_write`, `__wt_read`, `__wt_fsync`, `__wt_ftruncate`, `__wt_fs_rename/remove/directory_list`), WiredTiger buffers/scratch allocation, checksums, endian helpers, capacity throttling, compressors, encryptors, hot backup locks, checkpoint signaling, and connection flags.

## Risks and Edge Cases
- Slot state ordering is concurrency-critical. Incorrect barriers around `slot_state`, `log_close_fh`, or LSN updates can produce holes, stuck waits, premature file close, or false durability.
- Scanner corruption rules are intentionally subtle: zero-fill, backup copies, partial writes, and bad checksums have different recovery consequences.
- File-size and preallocation behavior can create logs larger than `file_max` in edge races; code attempts to minimize but not entirely eliminate that.
- Version/downgrade handling must avoid writing newer-format files before compatibility verification completes.
- Compression/encryption require matching configuration during recovery; missing codecs fail recovery with explicit guidance.
- `__log_write_internal` currently asserts `ret == 0` after slot-fill errors, so any future changes to write-error propagation need care.
- Directory fsync and file fsync are separated; losing a directory entry after rename is mitigated only when `sync_dir_lsn` is advanced.

## Test Signals
- Crash-recovery tests should cover partial writes, checksum mismatch, zero-filled preallocation, hole detection, and salvage.
- Backup tests should cover hot backup cursor interactions, backup file filtering, no rename/truncate while backup is active, and backup-copy checksum anomalies.
- Compatibility tests should cover log versions 1-5, downgrade forced checkpoint/removal, and unsupported future versions.
- Sync tests should verify `WT_LOG_FLUSH`, `WT_LOG_FSYNC`, `transaction_sync` modes, directory fsync on file rollover, and no hangs waiting for inactive new files.
- Compression/encryption tests should verify records can be scanned only with matching configuration and that small/unhelpful compression falls back cleanly.
