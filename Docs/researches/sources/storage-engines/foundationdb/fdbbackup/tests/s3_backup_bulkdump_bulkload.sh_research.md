# sources/storage-engines/foundationdb/fdbbackup/tests/s3_backup_bulkdump_bulkload.sh

## Purpose

`s3_backup_bulkdump_bulkload.sh` validates the newer BulkDump/BulkLoad backup path against traditional rangefile restore. It creates a backup in `both` snapshot mode so range files and SST files coexist, restores a traditional prefixed baseline, restores normal keys using BulkLoad when possible, and uses `audit_storage validate_restore` to compare results.

## Important APIs, Types, and Functions

Key functions are `restore_with_prefix_for_validation`, `run_validate_restore_audit`, `cleanup_validation_prefix`, and `test_bulkdump_bulkload`. `VALIDATION_PREFIX` is `\xff\x02/rlog/`, with end prefix `\xff\x02/rlog0`. `restore_with_prefix_for_validation` runs `fdbrestore start --add-prefix` with a validation tag and waits for completion. `run_validate_restore_audit` starts `audit_storage validate_restore "" \xff`, extracts the audit ID, retries transient errors, and polls `get_audit_status`. `test_bulkdump_bulkload` orchestrates data load, `run_backup` in `both` mode, prefixed rangefile restore, normal-key clear, BulkLoad or rangefile restore depending on encryption, audit comparison, cleanup, verification, encryption mismatch checks, blob cleanup, and log scanning.

## Control Flow

The script parses optional flags for encryption and partitioned-log coverage, including random variants. It sets a small data count, sources common test utilities, initializes provider environment, creates an encryption key when requested, starts a two-storage-server FDB cluster with BulkLoad-related knobs, and runs one blobstore URL test. The two-storage-server setup is intentional so BulkLoad can find a destination server distinct from the BulkDump source.

If encryption is enabled, BulkLoad validation is skipped because BulkLoad does not support encrypted backup data yet; the script falls back to rangefile restore and still verifies data and encryption mismatch behavior.

## State and Persistence Behavior

The script writes blobstore backup data, FDB cluster state, scratch logs, optional encryption key files, and temporary restored validation data under the system key prefix. It explicitly clears the validation prefix after audit or after encrypted fallback. Audit state is stored by the cluster audit subsystem and queried via `get_audit_status`.

## Dependencies and Integration Points

This script ties together `backup.cpp` snapshot mode `both`, restore mode `bulkload`, `Decode.h` prefix decoding, `BulkDumpCommand.cpp`/bulk dumping backend behavior, `AuditStorageCommand.cpp` validate-restore audit, blob credentials, MockS3/AWS fixtures, and shared backup helpers. It also depends on knobs `shard_encode_location_metadata`, `enable_read_lock_on_range`, and blobstore encryption configuration.

## Risks and Edge Cases

The audit ID is extracted by a 32-hex-character regex, so CLI output changes can break detection. Audit success is inferred from `Phase.*2` and failure from phases 3 or 4, making audit status formatting a test contract. Transient retry handling covers selected numeric errors only. Because validation data is restored into system keyspace, cleanup must run even after partial failures to avoid contaminating later tests. BulkLoad and encryption incompatibility is explicitly encoded as a skip, so encrypted runs do not validate BulkLoad equivalence.

## Test Signals

Passing this script signals that `both` backups produce usable rangefile and BulkDump/SST metadata, traditional prefixed restore works, BulkLoad restore can reproduce traditional restore output for plaintext backups, audit-based comparison succeeds, validation-prefix cleanup works, encryption mismatch failures still hold, and no Severity=40 errors occur.
