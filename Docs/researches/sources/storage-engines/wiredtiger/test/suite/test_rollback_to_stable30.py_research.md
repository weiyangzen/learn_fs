# sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable30.py

Purpose: validates that runtime RTS refuses to run while there are active file cursors or active transactions, including prepared transactions, and succeeds after resources are closed/resolved.

Important APIs/types/functions: direct `wttest.WiredTigerTestCase` subclass with `verify_rts_logs`. Uses `SimpleDataSet` and `ComplexDataSet`, row/string key formats, `prepare_resolve`, `assertRaisesWithMessage`, `conn.rollback_to_stable`, `prepare_transaction`, and commit/rollback callbacks.

Control flow: pins oldest/stable to 1, populates a dataset, opens a cursor and asserts RTS fails with an active-cursor message. Then it writes and prepares a transaction at timestamp 10, asserts RTS fails with an active-transaction message, resolves the prepared transaction by commit or rollback depending on test method, closes active resources, and verifies RTS succeeds.

State and persistence behavior: focuses on connection/session state rather than persisted data contents. Prepared transactions hold state that must block RTS until resolved.

Dependencies and integration points: integrates dataset variations, prepared transaction API, and error-message contracts for illegal RTS calls.

Risks: assertions depend on exact diagnostic regexes. ComplexDataSet adds coverage for multi-column schemas but can make setup heavier.

Test signals: expected `WiredTigerError` messages for active cursor/transaction and successful final `rollback_to_stable` for both commit and rollback resolution paths.
