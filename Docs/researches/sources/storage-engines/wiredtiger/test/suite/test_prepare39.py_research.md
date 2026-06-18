# sources/storage-engines/wiredtiger/test/suite/test_prepare39.py

## Purpose

Verifies history-store contents for a rolled-back prepared transaction under precise checkpoint and preserve-prepared.

## Important APIs, Control Flow, and State

The test commits value A at timestamp 21 and value B at 25 for keys 1 to 21, prepares key 21 at timestamp 30, advances stable to 30, verifies checkpoint writes prepared metadata, then rolls back at timestamp 35. A checkpoint with stable still 30 should place value B in the history store with max stop timestamp. After stable 40 and checkpoint/eviction, timestamp reads for key 21 at 21, 25, 30, and 35 return A/B/B/B as expected. After reopening, direct history-store reads expect value A with start 21 and stop 25.

## Dependencies, Risks, and Test Signals

Dependencies are direct history-store file cursors, with a disagg-specific shared history-store filename, preserve-prepared stats, and reopen. Risks are wrong HS stop timestamp when a prepared update is rolled back. Signals are direct HS tuple checks and timestamped user-data reads.
