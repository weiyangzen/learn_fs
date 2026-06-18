# sources/storage-engines/wiredtiger/src/include/timestamp_inline.h

Purpose: `timestamp_inline.h` supplies the mutation and predicate macros for `WT_TIME_WINDOW` and `WT_TIME_AGGREGATE`, plus inline getters for globally managed oldest, stable, and disaggregated schema timestamps.

Important APIs: time-window macros initialize, copy, compare, test start/stop/prepare presence, and set start/stop values from `WT_UPDATE` with prepared-rollback race handling. Time-aggregate macros initialize normal or merge accumulators, test emptiness, update from a time window or page delete, merge aggregates conservatively, normalize aggregates for obsolete-visible checks, and test whether stop data exists. Inline getters are `__wt_get_oldest_timestamp`, `__wt_get_stable_timestamp`, and `__wt_get_stable_disaggregated_schema_epoch`.

Control flow: update/read/reconciliation paths fill a `WT_TIME_WINDOW` from updates or cells, then feed it into `WT_TIME_AGGREGATE_UPDATE` while scanning keys or pages. Merge paths start with `WT_TIME_AGGREGATE_INIT_MERGE`, then choose max durable/newest values and min oldest-start values. Obsolete checks use `WT_TIME_AGGREGATE_MERGE_OBSOLETE_VISIBLE` to preserve the subtle distinction between all-deleted and partially-live pages.

State and persistence behavior: macros mutate caller-owned in-memory structs that often mirror persistent cell/page metadata. The getters read `WT_TXN_GLOBAL` booleans with acquire ordering before reading timestamp values; stable timestamp falls back to `recovery_timestamp` when no stable timestamp is published, while disaggregated schema epoch falls back to `WT_SCHEMA_EPOCH_NONE`.

Dependencies and integration points: depends on `WT_UPDATE`, `WT_PAGE_DELETED`, `WT_TXN_GLOBAL`, timestamp sentinels, atomic helpers, TSAN suppression, and visibility semantics in `txn_inline.h`. It integrates with update-chain reads, reconciliation, page deletion, checkpoint, rollback-to-stable, history store, disaggregated storage, and transaction timestamp APIs.

Risks: these are macros with repeated field access and no type safety beyond compile-time field names. Race handling around prepared rollback depends on reading saved transaction ids when an update txnid has become `WT_TXN_ABORTED`. Aggregate merge semantics are easy to misuse; in particular durable stop timestamp and `WT_TS_MAX` encode different concepts for obsolete checks.

Test signals: unit tests for empty/default predicates, prepared start/stop propagation, aborted prepared rollback races, page-delete aggregate updates, aggregate merge/all-deleted cases, getter ordering under concurrent timestamp publication, and rollback-to-stable/checkpoint suites that validate durable timestamp retention.
