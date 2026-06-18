# sources/storage-engines/wiredtiger/src/include/txn.h

Purpose: `txn.h` declares WiredTiger's transaction constants, sentinel ids/timestamps, rollback reason strings, visibility/isolation enums, shared transaction table entries, global transaction state, per-transaction operation records, snapshots, transaction time points, and per-session transaction context.

Important APIs and types: key sentinels include `WT_TXN_NONE`, `WT_TXN_FIRST`, `WT_TXN_MAX`, `WT_TXN_ABORTED`, `WT_TS_NONE`, `WT_TS_MAX`, and schema epoch sentinels. It defines checkpoint log flags, oldest-timestamp flags, timestamp-set flags, `WT_VISIBLE_TYPE`, `WT_OP_CONTEXT`, `WT_TXN_ISOLATION`, `WT_TXN_TYPE`, `WT_TXN_TRUNC_MODE`, `WT_TXN_SHARED`, `WT_PENDING_PREPARED_ITEM`, `WT_PENDING_PREPARED_MAP`, `WT_TXN_GLOBAL`, `WT_TXN_OP`, `WT_TXN_SNAPSHOT`, `WT_TXN_LOG`, `WT_TXN_TIME_POINT`, `WT_TXN`, and `WT_FIX_PREPARED_COOKIE`.

Control flow: transaction code publishes per-session state through `WT_TXN_SHARED`, tracks global current/oldest/durable/stable/pinned timestamps in `WT_TXN_GLOBAL`, stores per-operation undo/log/prepare metadata in `WT_TXN_OP`, and carries snapshot bounds plus active transaction ids in `WT_TXN_SNAPSHOT`. `WT_WITH_TXN_ISOLATION` temporarily forces isolation while asserting that transaction id and pinned state are restored safely.

State and persistence behavior: the structures are in-memory control state for MVCC, checkpoint, logging, prepared transactions, rollback-to-stable, and disaggregated schema epochs. They drive persistent effects by assigning transaction ids and timestamps to updates, page deletes, metadata, and log records. Prepared transaction maps can hold operations discovered from checkpoints for later claim/commit/rollback.

Dependencies and integration points: depends on cache-line padding, atomic/shared annotations, tail queues, btree/data-handle/session types, LSNs, item buffers, and timestamp definitions. It is the core contract consumed by `txn_inline.h`, transaction implementation files, checkpoint, logging, reconciliation, history store, recovery, cursor reads/writes, truncate, and prepared-discovery code.

Risks: sentinel ordering is fundamental: aborted must remain never visible, none must remain always visible, and max must represent end-of-time. Shared fields require precise memory ordering in inline code. The prepared transaction claim path swaps operation arrays, so ownership mistakes can double-free or leak operation state. Rollback reason strings are API-observable and should not change casually.

Test signals: transaction begin/commit/rollback suites, isolation matrix tests, prepared transaction recovery and claim tests, timestamp API tests, checkpoint visibility tests, rollback-to-stable, write-conflict tests, debug rollback injection, and assertions around `WT_WITH_TXN_ISOLATION` restoring shared pinned ids.
