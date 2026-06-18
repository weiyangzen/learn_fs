# sources/object-store/daos/src/vos/vos_dtx.c

## Purpose
`vos_dtx.c` implements VOS distributed transaction tracking. It manages active DTX allocation, durable prepare blobs, committed DTX blobs, availability checks for reads/updates/purge/migration, commit/abort transitions, membership refresh, reindex after container open, aggregation of old committed records, cleanup, local transactions, and DTX telemetry/statistics.

## Important APIs, Types, And Functions
- Active DTX entries use `struct vos_dtx_act_ent` in a volatile LRU array plus durable `struct vos_dtx_act_ent_df` records inside `DTX_ACT_BLOB_SIZE` blobs.
- Committed entries use volatile `struct vos_dtx_cmt_ent` btree records plus durable `struct vos_dtx_cmt_ent_df` records inside `DTX_CMT_BLOB_SIZE` blobs.
- `vos_dtx_table_register()` registers active and committed DTX dbtree classes.
- `vos_dtx_attach()`, `vos_dtx_register_record()`, `vos_dtx_prepared()`, and `vos_dtx_cleanup()` connect RPC/operation DTX handles to VOS mutations.
- `vos_dtx_check_availability()` maps DTX state to availability for fetch, update, punch, discard, purge, migration, and transactional reads.
- `vos_dtx_commit()` / `vos_dtx_commit_internal()` / `vos_dtx_post_handle()` commit one or more DTXs and update both durable committed blobs and volatile indexes.
- `vos_dtx_abort()` / `vos_dtx_abort_internal()` release records as aborted and remove active entries.
- `vos_dtx_check()`, `vos_dtx_load_mbs()`, `vos_dtx_refresh_mbs()`, `vos_dtx_set_flags()`, `vos_dtx_mark_committable()`, and `vos_dtx_mark_sync()` support DTX refresh/resync and corruption/orphan handling.
- `vos_dtx_act_reindex()` and `vos_dtx_cmt_reindex()` rebuild volatile indexes from durable blobs.
- `vos_dtx_aggregate()` compacts old committed blobs; `vos_dtx_cache_reset()` rebuilds volatile DTX caches; `vos_dtx_get_cmt_stat()` scans committed blobs for count and time statistics.

## Control Flow
The normal mutation path attaches a DTX handle through `vos_dtx_attach()`. If needed, `vos_dtx_alloc()` allocates an LRU slot, initializes DTX identity, epoch, flags, membership shape, sorted/unsorted ordering links, and inserts the active entry into the volatile active btree. Record modifications call `vos_dtx_register_record()`, which stores ilog/SVT/EVT offsets in inline or heap-backed arrays and marks the DTX active. On transaction end, `vos_dtx_prepared()` persists the active entry to the current active blob, extending the blob list if needed, writes membership and record arrays, sets `dae_preparing`, and later marks it prepared.

Commit first pins metadata buckets for evictable pools, starts an umem transaction with return-on-failure behavior, appends committed entries to committed blobs, calls `dtx_rec_release()` to mark ilog/SVT/EVT records committed, and commits the umem transaction. `vos_dtx_post_handle()` then updates telemetry, removes active btree/LRU entries, or marks entries committed/aborted if removal fails. Abort follows the same pin-and-transaction pattern but releases records with aborted state and posts removal as abort.

Availability checks first honor already committed/aborted DTX ids embedded in data records. For active DTXs, the function distinguishes purge/discard/default/update/punch/migration intents, owner visibility, corrupted/orphan flags, partial committed records, solo in-commit entries, membership refresh lists, and prepared-vs-initial states. Non-leader prepared entries can trigger server/client retry through `dtx_inprogress()`.

## State And Persistence Behavior
Durable DTX state is append-oriented. Active DTX blobs are linked from `vos_cont_df::cd_dtx_active_head/tail`; committed DTX blobs are linked from `cd_dtx_committed_head/tail`. Active blob entries contain identity, epoch, LID, flags, membership, dkey hash, and record offsets. Record offsets are tagged with DTX record type flags. Committing or aborting records updates ilog entries or `ir_dtx`/`dc_dtx` fields in SVT/EVT records and then invalidates active durable entries or frees whole blobs when empty. Committed blobs retain compact DTX reply-reconstruction history until aggregation removes old entries.

Volatile state includes active and committed btrees, DTX LRU array, active/sorted/unsorted/reindex lists, DTX handle backpointers, counts, telemetry gauges, and CoS/removal flags. Reindex on open reconstructs volatile active entries and committed index entries from durable blobs, including special handling for invalid, corrupted, orphan, partial committed, and old partial DTX records.

## Dependencies And Integration Points
The file is tightly integrated with umem transactions, DAOS btree, LRU array, ilog, single-value and evtree record descriptors, object cache eviction, bucket pinning/cache for evictable pools, container stable-epoch logic, telemetry, DTX membership structures, fail injection, and VOS aggregation. `vos_common.c` calls into `vos_dtx_prepared()`, validation, cleanup, and post handling from transaction end; iterators and upper layers call status and membership APIs for DTX refresh/resync.

## Risks And Edge Cases
- DTX state spans durable blobs and volatile indexes; partial failures can leave entries marked committed/aborted in memory until restart.
- The committed table may need to reuse old committed blobs under `-DER_NOSPACE`, trading reply-reconstruction history for forward progress.
- Solo DTX committing state is deliberately not treated as fully committed because subsequent fetch may not see data yet.
- Active DTX LID reuse requires epoch validation through the LRU array key and handle validation flags.
- Availability behavior is intent-specific; mistakes can expose uncommitted data, hide committed data, or block aggregation.
- Reindex must tolerate old partial DTX records, invalid durable entries, and non-strict historical epoch ordering.

## Test Signals
High-value tests include prepare/commit/abort for ilog/SVT/EVT records, multi-DTX commit with committed blob extension, committed blob reuse under no-space injection, solo DTX visibility, DTX availability for every intent, membership refresh and leader/non-leader behavior, corruption/orphan flags, invalid-record discard, cache reset and active/committed reindex after reopen, committed aggregation thresholds, evictable-pool bucket pinning, and local transaction object-cache eviction.
