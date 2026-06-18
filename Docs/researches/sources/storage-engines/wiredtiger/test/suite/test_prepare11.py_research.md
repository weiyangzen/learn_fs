# sources/storage-engines/wiredtiger/test/suite/test_prepare11.py

## Purpose

Exercises prepare resolution when a reserved update sits between two updates to the same key. It ensures repeated-key tracking does not skip either prepared operation during commit or rollback.

## Important APIs, Control Flow, and State

`test_prepare11` parameterizes column and string-row keys and whether the prepared transaction commits or rolls back. The test creates one table, begins a transaction, writes `value_x`, calls cursor `reserve()` on the same key, writes `value_y`, and prepares at timestamp 10. The commit path assigns commit timestamp 20 and durable timestamp 30 before commit; the rollback path calls `rollback_transaction`. No final read is needed: the test is a regression/crash assertion around prepare resolution over update/reserve/update chains.

## Dependencies, Risks, and Test Signals

Dependencies are `wttest`, `make_scenarios`, cursor reserve semantics, and transaction timestamp APIs. The risk is resolving only one prepared update because a reservation changes key-repeat metadata. The test signal is successful prepare resolution under both commit and rollback scenarios without assertion or write-chain corruption.
