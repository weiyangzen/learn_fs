# sources/storage-engines/wiredtiger/test/simulator/timestamp/src/session_simulator.cpp

Purpose: implements session transaction lifecycle and transaction timestamp semantics for the in-memory simulator.

Important APIs and control flow: `begin_transaction()` rejects already-running transactions, resets state, parses read timestamp and rounding config, sets read timestamp, then marks the transaction running. `timestamp_transaction()` and `timestamp_transaction_uint()` set commit/durable/prepare/read timestamps after validation. `prepare_transaction()` requires a running transaction, a prepare timestamp, no prior commit timestamp, and marks the transaction prepared. `commit_transaction()` parses optional commit/durable timestamps, rolls back on earlier transaction errors, enforces prepared versus non-prepared requirements, updates global durable timestamp, and ends the transaction. `rollback_transaction()` clears running state. Query returns selected session timestamp as hex.

State and persistence behavior: all state is in session fields. Commit and durable setters maintain first commit timestamp, default durable-to-commit behavior, durable-set flag, and rounding behavior around prepare/read timestamps.

Dependencies and integration points: depends on `connection_simulator` for global timestamp state, `timestamp_manager` for validation and parsing, and `error_simulator` for return/error macros.

Risks: failed timestamp operations set `_txn_error`, causing the next commit to roll back; callers must understand this deferred behavior. Some unsupported WiredTiger config keys are silently ignored by being listed as unsupported. Prepared/non-prepared durable timestamp rules are simplified to simulator needs.

Test signals: call-log replay should match WiredTiger return codes for transaction timestamp operations and query timestamps for commit, first_commit, prepare, and read.
