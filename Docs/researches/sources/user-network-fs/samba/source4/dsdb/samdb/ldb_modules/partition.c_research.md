# sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/partition.c

## Purpose

`partition.c` is the runtime router for Samba DSDB partitioned LDB databases. It decides which backend partition receives each request, fans searches or extended operations out to multiple partitions when required, replicates configured special DNs to all partitions, enforces cross-partition rename rules, and coordinates transactions, commit preparation, aborts, read locks, and global sequence-number requests across the primary metadata DB, partition backends, and `metadata.tdb`.

This file is the core execution half of the partition module; `partition_init.c` builds the partition list and `partition_metadata.c` supplies the metadata TDB used for locking and sequence numbers.

## Important APIs and Types

`struct partition_context` tracks a logical caller request split into one or more partition requests. It holds the original request, the generated per-partition requests, completion counts, and queued referrals.

`struct part_request` pairs a target module with the cloned request to run there.

`partition_request()` wraps `ldb_next_request()` with optional trace logging showing the current partition control.

`find_partition()` chooses a `dsdb_partition` by DN, honoring `DSDB_CONTROL_CURRENT_PARTITION_OID` when supplied by upstream modules such as replication metadata.

`partition_prep_request()` clones a search/add/modify/delete/rename/extended request for a specific partition, preserves caller controls except current-partition handling, adds `DSDB_CONTROL_CURRENT_PARTITION_OID` when appropriate, and adjusts a search base to the partition root if the caller searched above that partition.

Request handlers are `partition_search()`, `partition_add()`, `partition_modify()`, `partition_delete()`, `partition_rename()`, and `partition_extended()`.

Transaction and locking APIs exported to the module ops are `partition_start_trans()`, `partition_prepare_commit()`, `partition_end_trans()`, `partition_del_trans()`, `partition_read_lock()`, and `partition_read_unlock()`.

Sequence helpers include `partition_primary_sequence_number()`, `partition_sequence_number_from_partitions()`, and `partition_sequence_number()`.

## Control Flow

For writes, `partition_add()`, `partition_modify()`, and `partition_delete()` delegate to `partition_replicate()`. If a special DN appears in the configured replicate list, `partition_copy_all()` sends the operation to the primary chain, then `partition_copy_all_callback_action()` fetches the resulting object and add/modifies or deletes it in every partition so replicated metadata stays aligned. Otherwise `partition_replicate()` finds the target partition and prepares one request for that backend; unmatched DNs fall through to the main LDB chain.

`partition_rename()` finds the old and new partitions before routing. If the rename crosses partition boundaries, it returns `LDB_ERR_AFFECTS_MULTIPLE_DSAS`; otherwise it routes based on the old DN.

Search routing is more complex. `partition_search()` first honors explicit current-partition controls. It then interprets domain-scope, phantom-root, and no-global-catalog controls, clearing handled search-option bits before forwarding. Special DNs and uninitialized state pass through. Empty-base searches require phantom-root and otherwise fail. With phantom-root, the module matches exact partition roots, parent searches over partition roots, and child searches under a partition. Without phantom-root, it finds the containing partition and may generate LDAP referrals for child partitions unless domain-scope or BASE scope suppresses them. Partial-replica partitions are skipped when `DSDB_CONTROL_NO_GLOBAL_CATALOG` makes them invisible.

`partition_req_callback()` multiplexes replies. Entries and referrals are forwarded immediately. Done replies advance to the next prepared partition request, and only the final done completes the original request. If a current-partition control exists and the operation is single-partition or an entry reply, it adds that control to the reply so upstream modules can identify the backend used.

`partition_extended()` handles schema-update-now by incrementing metadata schema sequence, handles LDB sequence-number requests from `metadata.tdb`, creates partitions via `partition_create()`, and otherwise fans extended operations out to all partitions.

## State and Persistence Behavior

Runtime state comes from `struct partition_private_data` defined in `partition.h`: sorted partition list, replicate-DN list, metadata handle, module selection records, metadata sequence, transaction nesting count, optional forced module config, and backend store type.

Transactions are global across all backends. Start order is metadata.tdb transaction, top-level DB transaction, reload partition metadata, then each partition transaction. Prepare order matches start order. End/abort order is reverse for partition DBs, then top-level DB, then metadata.tdb. The comments explain why metadata.tdb is used as the effective global lock: TDB read/write locks block each other in the way MDB locks do not, and sequence updates force meaningful prepare-commit locking.

Read locks follow the same ordering: reload partition metadata first, then metadata.tdb read lock, top-level DB read lock, then each partition read lock. Unlock reverses that order.

Global sequence numbers are served from `metadata.tdb` through `partition_metadata_sequence_number()` and `partition_metadata_sequence_number_increment()`. Older sum-of-partitions logic remains as migration/fallback helper.

## Dependencies and Integration Points

This file is tightly integrated with LDB module ops, DSDB partition controls, LDB search-option controls, loadparm DNS domain settings for referrals, DSDB extended operations, transaction/read-lock module callbacks, and the initialization/metadata helpers declared through `partition_proto.h`.

It assumes the partition list is sorted by DN so search routing can stop after the nearest matching partition. It relies on `partition_init.c` for partial-replica flags and replicate DN lists and on `partition_metadata.c` for lock/sequence semantics.

## Risks and Edge Cases

Lock ordering is the highest-risk area. Any new path that locks a backend outside the documented metadata/top-level/partition order can deadlock or expose inconsistent cross-partition reads.

`partition_read_lock()` has a failure path that unlocks partition and top-level DB locks but does not explicitly call `partition_metadata_read_unlock()` after a metadata lock succeeds and a later lock fails. That may be intentional or covered by surrounding semantics, but it is a code path worth targeted review because the success path always expects metadata unlock in `partition_read_unlock()`.

Search referral generation depends on string containment checks against DN text to remove less-specific referrals. DN formatting or escaping changes could affect referral pruning.

Cross-partition copy-all for special DNs performs synchronous add/modify/delete operations after the primary request completes. Failures midway can leave partitions inconsistent unless the surrounding transaction reliably aborts all touched backends.

The module allows unmatched non-special write DNs to fall through to the main LDB chain, with a TODO suggesting an error might be more appropriate. Changes there could affect provisioning and special internal records.

The current-partition control affects routing and reply metadata; incorrect control data can force operations to unexpected partitions.

## Test Signals

Tests should cover single-partition writes, special-DN replication to all partitions, deletion of special DNs, modify operations that delete attributes, cross-partition rename rejection, phantom-root searches, domain-scope suppression of referrals, empty-base behavior with and without phantom-root, no-GC behavior with partial replicas, current-partition control routing and reply controls, extended operation fan-out, schema update sequence increments, metadata-backed sequence number next/highest, transaction rollback after a partition start failure, prepare/end failure propagation, and read-lock/read-unlock ordering under concurrent readers and writers.
