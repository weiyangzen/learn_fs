# sources/storage-engines/tikv/components/cdc/tests/integrations/test_cdc.rs

## Purpose
This is the broad CDC integration regression suite for TiKV's change-data service. It drives a simulated Raftstore cluster through transactional KV, raw KV, region topology, timestamp, old-value, filter, flashback, and overlapped-write scenarios, then asserts the `ChangeData` gRPC stream emits the expected `cdcpb::Event` rows, resolved-ts messages, and region errors. The same core tests are run against `ApiVersion::V1` and `ApiVersion::V2` through `test_kv_format_impl!`, with ApiV2 keys deliberately using the txn/raw key prefixes required by the test format.

## Important APIs, Types, And Functions
The file consumes `TestSuite`, `TestSuiteBuilder`, `new_event_feed`, and `new_event_feed_v2` from the CDC test module. It uses TiKV RPC requests and protobuf event types such as `ChangeDataRequest`, `Event_oneof_event`, `EventLogType`, `EventRowOpType`, `ExtraOp`, `ChangeDataRequestKvApi`, `Mutation`, `PrewriteRequest`, `CommitRequest`, and `BatchRollbackRequest`. It also uses cluster control helpers from `test_raftstore`, PD TSO access through `PdClient`, `ConcurrencyManager` memory locks, `Task::Validate`/`Validate` hooks into the CDC endpoint, and `CDC_RESOLVED_TS_ADVANCE_METHOD` for resolved-ts mode verification.

The tests cover these major behaviors:

- Subscription lifecycle: `test_cdc_basic`, `test_cdc_not_leader`, `test_region_split`, `test_duplicate_subscribe`, `test_cdc_cluster_id_mismatch`, and `test_cdc_stale_epoch_after_region_ready`.
- Initial/incremental scans: `test_cdc_scan`, `test_cdc_rawkv_scan`, `test_cdc_scan_ignore_gc_fence`, and `test_prewrite_without_value`.
- Event streaming for txn/raw operations: basic prewrite/commit/rollback, raw put/CAS/delete, batch-size splitting, and 1PC committed events.
- Old-value extraction: `test_old_value_basic`, multi-changefeed old-value behavior, cache-hit counters, pessimistic old-value reads, and 1PC old values.
- Resolved timestamp behavior: TSO failures, concurrency-manager locks, cluster upgrading, learner peers, partial subscriptions, region creation, term changes, and flashback blocking.
- Filtering: `filter_loop`, key-range filtering, txn-source rollback behavior, and v2 stream multiplexing.
- Edge cases around missing writes, GC fences, overlapped rollback/write records, and stale CDC lock-tracker state.

## Control Flow
Most tests follow the same structure. A simulated cluster is built, a `ChangeDataRequest` is created with region epoch and TiCDC feature headers, the request is sent through a duplex gRPC stream, and the first event is usually asserted to be `Initialized`. The test then mutates the store through TiKV RPCs or cluster topology operations and repeatedly calls the `receive_event` closure until the relevant row or resolved-ts signal appears. Region leadership and split tests use `Task::Validate(Validate::Region(...))` to inspect the endpoint delegate after stream registration or after an error.

The scan tests preload MVCC versions before subscription, then assert CDC backfill order and batching before `Initialized`. `checkpoint_ts` is varied to make only later versions appear. RawKV tests set `kv_api` to `RawKv`, flush causal timestamps when needed, and assert `Committed` rows rather than transactional prewrite/commit pairs. Old-value tests enable `ExtraOp::ReadOldValue` even though some assertions document that the field is now effectively ignored for downstream behavior, then check `old_value` on prewrite or committed rows. Resolved-ts tests keep resolved-ts events instead of filtering them out and assert monotonicity, blocking at memory locks or flashback, and eventual advancement after unblock.

Several late-file tests are bug reproductions. They construct overlapping timestamp relationships where one transaction's `commit_ts` equals another transaction's `start_ts`, rollback a secondary key so no CF_WRITE rollback is generated, then ensure CDC remains active when a later prewrite encounters a stale lock-tracker entry. `test_verify_overlapped_write_skips_cf_write` is a minimal storage-side confirmation of that skipped CF_WRITE behavior.

## State And Persistence Behavior
The suite mutates real in-memory test engines through TiKV RPC paths, so state exists in MVCC lock/write/default column families, Raftstore metadata, PD region metadata, and CDC endpoint delegate state. Persistent behaviors under test include lock insertion/removal, committed writes, rollback writes or omitted rollback writes, GC fence effects, raw KV entries, flashback deletes, and resolved-ts advancement derived from PD TSO and concurrency manager state. CDC-specific state includes registered downstreams, per-region delegates, old-value cache counters, lock tracking, feature-gated resolved-ts strategy, request key ranges, and stream multiplexing request IDs.

## Dependencies And Integration Points
The file is tightly integrated with the simulated Raftstore stack, TiKV client protobufs, CDC endpoint scheduler, PD mock client, causal timestamp provider, concurrency manager, and API-version key encoders. The gRPC stream is the public integration surface, while `Task::Validate` is an internal test-only inspection path. Several tests rely on exact behavior from the storage transaction layer, including pessimistic lock/prewrite semantics, `check_txn_status`, async-commit-like overlapped rollback handling, 1PC responses, and flashback RPCs.

## Risks
The suite is timing sensitive. It uses sleeps, receive timeouts, and retry loops around registration and resolved-ts movement, so raft scheduling delays can cause flakiness if intervals change. Many assertions depend on test cluster defaults such as batch scan size set in `TestSuiteBuilder`, feature gate versions, generated TSO ordering, and key prefixes under ApiV2. Some tests use direct timestamps like `10`, `15`, or relationships like `start_ts == commit_ts`; changing timestamp allocation or transaction validation can break them in non-obvious ways. The overlapped-write bug tests are especially subtle because the expected storage behavior is absence of a rollback write, so the CDC signal is mostly "delegate remains active".

## Test Signals
This file is itself an integration test signal for CDC. It verifies event types, keys, values, old values, commit/start timestamps, region errors (`not_leader`, `epoch_not_match`, `cluster_id_mismatch`, duplicate request), resolved-ts monotonicity and region sets, cache hit/miss counters, downstream delegate lifecycle, and active/failed delegate status. Coverage is broad across V1/V2 transactional CDC and RawKV, but it is still a simulated-cluster suite rather than a real multi-node deployment test.
