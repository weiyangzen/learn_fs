# sources/storage-engines/wiredtiger/src/log/log_sys.c

## Purpose
Builds and writes logging system records and provides a verbose diagnostic dump of the logging subsystem.

## Important APIs, Types, and Functions
`__wt_log_system_backup_id` writes incremental-backup ID state as a `WT_LOGREC_SYSTEM` record. `__wti_log_system_prevlsn` writes a fixed-size previous-LSN system record directly to a chosen log file handle. `__wti_log_recover_prevlsn` unpacks that operation during recovery. `__wt_verbose_dump_log` prints log-manager flags, paths, sizes, sync policy, version, file number, and key LSNs.

## Control Flow
Backup-ID logging exits early unless logging and incremental backup are enabled and the log version supports system records. It packs a system record header, then iterates `WT_BLKINCR_MAX`, packing either each valid ID/granularity or an empty sentinel. Previous-LSN logging builds an aligned record, computes its checksum manually, activates a temporary slot, overrides its file handle, and calls the log fill routine without compression or encryption.

## State and Persistence Behavior
The backup-ID record persists the connection's incremental backup slots in the log so recovery can restore or stop IDs. The previous-LSN record persists a prior LSN marker at a log boundary. The verbose dump is read-only diagnostic output.

## Dependencies and Integration Points
This file depends on log record allocation/packing helpers, backup-ID log operation packing, previous-LSN packing/unpacking, checksum/byteswap helpers, and the slot fill path. Recovery consumes `__wti_log_recover_prevlsn`, while incremental backup and checkpoint/switch logic use the backup ID writer.

## Risks and Edge Cases
The system record path must stay compatible with `log->log_version`. Invalid incremental backup slots are deliberately written with `UINT64_MAX` granularity and an empty string, so recovery code must preserve that sentinel meaning. `__wti_log_system_prevlsn` bypasses the normal log-write path and must maintain alignment, checksum, and endian handling exactly.

## Test Signals
Incremental backup tests should verify ID persistence across restart, force-stop behavior, and recovery from system log records. Recovery tests should cover previous-LSN unpacking. Verbose logging tests or diagnostics can validate expected dump fields under enabled and disabled logging.
