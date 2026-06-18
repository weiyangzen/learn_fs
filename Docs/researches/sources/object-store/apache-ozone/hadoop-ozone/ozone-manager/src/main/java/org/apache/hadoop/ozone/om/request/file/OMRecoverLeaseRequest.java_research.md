# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/file/OMRecoverLeaseRequest.java

## Purpose

`OMRecoverLeaseRequest` starts recovery for an hsync/open FSO file lease. It marks the open key as under recovery, refreshes last-block pipeline/token information, and returns both closed key and open key metadata for recovery clients.

## Important APIs, Types, And Functions

- Constructor extracts volume, bucket, key, and force flag from `RecoverLeaseRequest`.
- `preExecute(OzoneManager)` is disallowed until `HBASE_SUPPORT`, normalizes the key, and checks key `WRITE` ACL.
- `validateAndUpdateCache(...)` locks the bucket, validates bucket/volume, delegates to `doWork`, writes an `OMRecoverLeaseResponse`, and audits `RECOVER_LEASE`.
- `doWork(...)` locates the FSO key, validates hsync metadata, resolves the open-file key by writer ID, enforces soft lease limit unless forced, marks `LEASE_RECOVERY`, updates the open-key cache, refreshes block pipeline/token data, and builds `RecoverLeaseResponse`.
- `updateBlockInfo(...)` refreshes block token and SCM pipeline for relevant last blocks.

## Control Flow And State

The request targets only `FILE_SYSTEM_OPTIMIZED` layout. It uses `OmFSOFile` to derive file/open-file DB keys. The closed key table row must exist and carry `HSYNC_CLIENT_ID`; otherwise the file is treated as closed or missing. The open-key row must exist and not be deleted. If already under recovery, the operation is idempotent; otherwise it checks the configured lease soft limit, adds `LEASE_RECOVERY=true`, updates modification time/update ID, and writes the open-key table cache entry.

## Dependencies And Integration Points

It integrates with FSO metadata key builders, open-key/key tables, hsync metadata constants, SCM container pipeline lookup, gRPC block token generation, layout feature gating, OM metrics, and `OMRecoverLeaseResponse`.

## Risks And Test Signals

Tests should cover forced and non-forced soft-limit behavior, missing closed key, already closed key, missing open key, deleted open key, already-under-recovery idempotency, token generation when enabled, pipeline refresh, metadata mutation, lock/audit behavior, and layout-feature gating.
