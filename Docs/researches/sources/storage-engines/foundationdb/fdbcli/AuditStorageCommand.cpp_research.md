# sources/storage-engines/foundationdb/fdbcli/AuditStorageCommand.cpp

## Purpose

`AuditStorageCommand.cpp` implements the `fdbcli audit_storage` command family. It starts or cancels cluster storage audits for high availability, replica consistency, location metadata, storage-server shards, restore validation, and metadata encoding.

## Important APIs, Types, and Functions

`auditStorageCommandActor` maps command tokens to `AuditType` values and returns the relevant audit `UID`. Startable audit types include `ValidateHA`, `ValidateReplica`, `ValidateLocationMetadata`, `ValidateStorageServerShard`, `ValidateRestore`, and `ValidateMetadataEncoding`. Cancel supports the first five distributed audit types. For HA and replica audits, an optional storage engine filter is parsed through `KeyValueStoreType::fromString` and restricted to `SSD_BTREE_V2`, `SSD_ROCKSDB_V1`, and `SSD_SHARDED_ROCKSDB`. `auditStorageFactory` registers help.

## Control Flow

With `audit_storage cancel <type> <id>`, the actor validates token count, maps the type, parses the UID, and calls `cancelAuditStorage` with a 60-second timeout. For start commands, it maps the type, optionally handles `metadata_encoding` as a client-side scan via `checkMetadataEncodingCommandActor`, parses begin/end key arguments, validates `end <= allKeys.end` and `begin < end`, optionally parses the engine filter, and calls `auditStorage` with the key range and timeout.

## State and Persistence Behavior

Distributed audits are persisted through FoundationDB management APIs and later observed by `get_audit_status`. Cancelling mutates audit state for the specified audit ID. The metadata encoding path creates a synthetic local audit ID but performs client-side validation rather than submitting a distributed audit.

## Dependencies and Integration Points

The file depends on `ManagementAPI.h`, `NativeAPI.actor.h`, and `Audit.h`. It integrates directly with backup/restore validation: `s3_backup_bulkdump_bulkload.sh` uses `audit_storage validate_restore "" \xff` after restoring a traditional prefixed baseline and a BulkLoad result, then polls `get_audit_status validate_restore id <AuditID>`.

## Risks and Edge Cases

Token count handling differs by audit type: most audits can use default full range, one begin key, begin/end, or begin/end/engine for selected types. Invalid ranges silently fall back to usage output and empty UID. `UID::fromString` is not guarded locally, so malformed cancel IDs depend on lower-level behavior. `ValidateMetadataEncoding` is start-only, not cancelable through this branch. Help text includes the supported engine and type names and is therefore a compatibility surface.

## Test Signals

The BulkDump/BulkLoad script is a direct integration test for `ValidateRestore`. It expects the command to print a 32-hex-character audit ID, and it treats audit phase 2 as success. Additional tests should cover cancel paths, invalid ranges, unsupported engine filters, and metadata encoding behavior.
