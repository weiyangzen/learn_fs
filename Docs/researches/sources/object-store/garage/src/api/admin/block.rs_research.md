# sources/object-store/garage/src/api/admin/block.rs

Purpose: implements local block administration endpoints for inspecting resync errors, block references/backlinks, retrying resync, and purging blocks plus associated metadata references.

Important handlers/functions: `LocalListBlockErrorsRequest` maps block manager resync errors into API rows. `LocalGetBlockInfoRequest` resolves a block hash prefix, reads refcount and block reference table entries, and joins version/MPU/object backlinks. `LocalRetryBlockResyncRequest` clears backoff for all errored blocks or a provided list. `LocalPurgeBlocksRequest` marks versions and block refs deleted and may add object delete markers or delete MPU records. Helpers are `find_block_hash_by_prefix` and `handle_block_purge_version_backlink`.

Control flow and state: local persistent state spans block manager reference counts/resync queue, `block_ref_table`, `version_table`, `mpu_table`, and `object_table`. Purge walks requested hashes, marks block refs deleted, marks versions deleted, clears MPU parts when needed, and inserts a delete marker if the purged version is the latest complete object version.

Dependencies/integration: depends on Garage block manager, S3 object/version/MPU models, table range/get/insert APIs, hash parsing, common error helpers, and local admin RPC wrappers generated in `api.rs`.

Risks: purge is destructive metadata surgery and must preserve table convergence through tombstones rather than raw deletion. Prefix lookup requires at least four characters and scans the underlying block-ref store; ambiguous prefixes fail. `LocalGetBlockInfo` limits range reads to 10000 refs. Object delete-marker insertion uses `timestamp + 1`, which assumes monotonic ordering is sufficient for hiding purged latest versions.

Test signals: cover prefix validation/ambiguity, blocks with object backlinks, MPU backlinks present and garbage-collected, retry all vs selected blocks, purge idempotency, deleted refs/versions, latest-version delete marker insertion, and large ref fanout behavior near the 10000 limit.
