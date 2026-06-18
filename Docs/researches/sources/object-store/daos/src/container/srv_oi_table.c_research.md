# sources/object-store/daos/src/container/srv_oi_table.c

## Purpose
Builds a snapshot object index table (OIT) by enumerating VOS object IDs in a target container at a snapshot epoch and writing those IDs into a special DAOS object. This supports snapshot/OIT operations initiated by `srv_epoch.c`.

## Important APIs and types
- `OID_SEND_MAX` limits batched OID updates per bucket to 128.
- `struct oit_bucket` stores a heap array of OIDs and a count for one OIT bucket.
- `struct oit_scan_args` carries local pool/container/object handles, target OIT object ID, previous OID suppression state, bucket count, IOD/SGL scratch arrays, and per-bucket arrays.
- `cont_child_gather_oids()` is the exported target-side entry point declared in `srv_internal.h`.

## Control flow
`cont_child_gather_oids()` allocates scan state and one OID array per possible bucket, fetches pool service ranks from IV, opens a client-side pool handle, opens the container using the same container handle UUID as snapshot creation, reads the container global version, and opens the OIT object for update. It iterates VOS objects over the exact snapshot epoch with `VOS_IT_FOR_MIGRATION`. `cont_iter_obj_cb()` ignores OIT objects, suppresses adjacent duplicate public OIDs caused by shard variants, hashes OIDs into buckets, and flushes full buckets with `cont_send_oit_bucket()`. After iteration, all nonempty buckets are flushed.

## State and persistence behavior
The source container state is VOS object metadata at one epoch. The generated OIT is persisted as DAOS object updates: each bucket is a dkey and each object ID is an akey with the snapshot epoch as the value. For old container global versions, all OIDs use one bucket; newer versions can use `DAOS_OIT_BUCKET_MAX`.

## Dependencies and integration
Depends on VOS iteration, DAOS client-side pool/container/object APIs (`dsc_pool_open`, `dsc_cont_open`, `dsc_obj_open`, `dsc_obj_update`), pool IV service rank fetch, object ID helpers, and OIT key macros. It is invoked from `srv_target.c` during `CONT_TGT_SNAPSHOT_NOTIFY` when snapshot options request OIT work.

## Risks
The code comments note that updates use epoch 0 rather than the snapshot epoch for OIT object writes, which can cause overwrites/space inefficiency across targets. Duplicate suppression assumes same public OIDs are adjacent in VOS iteration. The final flush loop overwrites `rc` on each bucket and does not break on first failure, so an earlier flush error can be hidden by a later success. OID arrays are large and heap-managed; allocation failure must clean up partially initialized buckets.

## Test signals
Tests should cover empty containers, duplicate shard OIDs, old versus new global versions, bucket hashing and full-bucket flushing, OIT object exclusion, VOS iteration failures, DAOS update failures in mid/final flushes, and cleanup of all handles/rank lists/bucket arrays.
