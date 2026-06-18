# sources/storage-engines/wiredtiger/test/simulator/timestamp/src/include/session_simulator.h

Purpose: declares the session-level transaction timestamp simulator API and per-transaction state.

Important APIs and control flow: public API methods mirror WiredTiger session operations: `begin_transaction`, `rollback_transaction`, `prepare_transaction`, `commit_transaction`, `timestamp_transaction`, `timestamp_transaction_uint`, and `query_timestamp`. Accessors expose commit, durable, first commit, prepare, and read timestamps plus flags for prepared/running/rounding states. Private setters and config decoding enforce validation through `timestamp_manager`.

State and persistence behavior: per-session state tracks whether a transaction is running/prepared, whether commit/durable/read timestamps are set, rounding flags, transaction error flag, and timestamp values. `reset_txn_level_var()` resets all transaction-level state.

Dependencies and integration points: used by `connection_simulator`, `timestamp_manager`, and both frontends. Copy and assignment are deleted so sessions are owned by connection.

Risks: all state is single-threaded and mutable; concurrent use would need synchronization. The boolean/timestamp split must remain consistent for query and validation behavior.

Test signals: replayed call logs should validate begin/prepare/commit/rollback sequencing and timestamp query values.
