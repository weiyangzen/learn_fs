# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/key/OMAllocateBlockRequest.java

## Purpose

`OMAllocateBlockRequest` allocates an additional block for an open key. It is used by streaming writes after initial key/file creation and updates the open-key table with the new block location while enforcing bucket quota and lease-recovery constraints.

## Important APIs, Types, And Functions

- `preExecute(OzoneManager)` normalizes the key, rebuilds an `ExcludeList`, allocates one SCM block with tokens if configured, stamps modification time, checks open-key write ACLs, preserves client ID/exclude list, and embeds the allocated block in the request.
- `validateAndUpdateCache(OzoneManager, ExecutionContext)` validates volume/bucket, locates open key, rejects missing/deleted/overwritten/lease-recovery open keys, quota-checks existing plus newly allocated space, appends the block, updates modification time/update ID, writes open-key cache, and returns `OMAllocateBlockResponse`.
- Protected methods `getOpenKeyInfo`, `getOpenKeyName`, `addOpenTableCacheEntry`, and response factories are overridden by FSO.
- Validators reject EC requests before finalization and old-client operations on unsupported bucket layouts.

## Control Flow And State

PreExecute allocates from SCM before full metadata validation, a documented tradeoff. Validate initially avoids locks while locating the open key, then acquires the bucket write lock for quota and cache mutation. It computes total allocated space from existing and new block counts using `QuotaUtil` and the open key's replication config, appends one block, writes a cache entry to the open-key table, and audits outside the lock.

## Dependencies And Integration Points

The class depends on SCM block allocation, block tokens, `ExcludeList`, open-key table APIs, quota utilities, hsync metadata constants, `OMAllocateBlockResponse`, request validation, OM metrics, and ACL checks against the open key.

## Risks And Test Signals

Tests should cover missing open key, lease recovery, deleted/overwritten hsync metadata, quota failures, modification time/update ID updates, block-token/exclude-list propagation, old-client/EC gates, response block location, and lock detail propagation. Race behavior with bucket delete/rename is intentionally deferred to commit and should be documented in tests.
