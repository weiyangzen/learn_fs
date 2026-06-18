# sources/storage-engines/wiredtiger/test/suite/test_prepare30.py

## Purpose

Validates prepare API error handling when `preserve_prepared=true` is enabled.

## Important APIs, Control Flow, and State

The scenario enables `precise_checkpoint=true,preserve_prepared=true`. The test sets stable timestamp 50, creates a simple table, begins a transaction, and calls `prepare_transaction` at timestamp 100 without a `prepared_id`. It expects `WiredTigerError` with the message requiring `prepared_id` when preserve prepared is enabled.

## Dependencies, Risks, and Test Signals

Dependencies are `make_scenarios`, preserve-prepared connection config, and `assertRaisesWithMessage`. The risk is accepting prepared transactions without durable identity metadata needed by preserve-prepared checkpoint/recovery. The test signal is the precise API validation failure.
