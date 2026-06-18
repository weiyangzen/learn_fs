# sources/storage-engines/wiredtiger/src/include/timestamp.h

Purpose: `timestamp.h` defines the core time-window and time-aggregate structures that encode transaction ids, commit/durable timestamps, stop timestamps, and prepare metadata for values, tombstones, pages, and reconciled aggregates.

Important APIs and types: string buffer constants include `WT_TS_HEX_STRING_SIZE`, `WT_TS_INT_STRING_SIZE`, and `WT_TIME_STRING_SIZE`. `WT_TIME_WINDOW` stores durable/start/prepare/start transaction fields plus durable/stop/prepare/stop transaction fields. `WT_TIME_AGGREGATE` stores newest start/stop durable timestamps, oldest start timestamp, newest transaction, newest stop timestamp and transaction, prepare marker, and `init_merge`.

Control flow and state: this header is declarative; mutation is performed by `timestamp_inline.h`, transaction code, reconciliation, history-store code, and page-delete logic. The defaults are semantically important: no start is `WT_TXN_NONE`/`WT_TS_NONE`, no stop is `WT_TXN_MAX`/`WT_TS_MAX`, and prepared ids default to `WT_PREPARED_ID_NONE`.

Persistence behavior: these structures are part of WiredTiger's MVCC and history metadata model. Time windows can be materialized into on-disk cells/pages, and time aggregates summarize page-level visibility for reconciliation, eviction, checkpoint, rollback-to-stable, and obsolete-history decisions.

Dependencies and integration points: depends on timestamp and transaction sentinel constants from `txn.h`. It integrates tightly with `txn_inline.h` visibility checks, `timestamp_inline.h` macros, cell unpacking, reconciliation time aggregation, history-store lookup, rollback-to-stable, and checkpoint stable/oldest timestamp rules.

Risks: sentinel values carry meaning, so changing `WT_TS_MAX`, `WT_TXN_MAX`, or default initialization semantics would affect visibility and obsolete detection. Durable timestamps must be treated conservatively because content cannot be discarded merely because commit timestamp is old. Prepared metadata must be propagated consistently or readers can miss prepare conflicts.

Test signals: timestamp format tests, time-window encode/decode tests, checkpoint/recovery with prepared updates and tombstones, rollback-to-stable tests that rely on newest durable timestamps, and reconciliation tests that verify page aggregates for all-live, all-deleted, prepared, and mixed windows.
