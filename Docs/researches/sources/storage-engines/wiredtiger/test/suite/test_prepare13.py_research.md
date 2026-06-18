# sources/storage-engines/wiredtiger/test/suite/test_prepare13.py

## Purpose

Verifies fast truncate fails with a conflict when the truncation range contains a prepared update.

## Important APIs, Control Flow, and State

`test_prepare13` builds a large timestamp-capable table with small page sizes, loads many records, prepares a replacement at key 1000, advances stable/oldest to the prepare timestamp, then updates many later records from a separate session to encourage eviction of the prepared page. A separate transaction attempts `session.truncate` from key 100 through the table end and expects `WiredTigerError` matching `/conflict between concurrent operations/`. The prepared transaction is resolved in a `finally` block with commit and durable timestamps 50.

## Dependencies, Risks, and Test Signals

Dependencies include `simple_key`, `simple_value`, `make_scenarios`, explicit truncate cursors, and WiredTiger error assertions. The risk is fast-truncate bypassing page-level prepared-update checks. The test signal is the expected conflict rather than silent range deletion.
