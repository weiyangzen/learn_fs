# sources/storage-engines/wiredtiger/test/suite/test_layered_stepup08.py

## Purpose
Tests draining of the layered ingest table during follower-to-leader promotion for inserts, updates, removes, and remove/insert ordering.

## APIs, Types, And Functions
Defines `test_layered_stepup08` with small and large scenarios. It uses `helper_disagg.Oplog` to generate and apply logical operations, `disagg_advance_checkpoint`, connection role reconfiguration, stable timestamps, checkpoints, and direct transactions for a tombstone-chain edge case.

## Control Flow, State, And Persistence
Most tests create leader and follower copies of one layered table, apply oplog ranges, advance checkpoints, promote the follower, make the last oplog timestamp stable, and checkpoint to drain ingest state. Three tests intentionally call `skipTest` after the drain checkpoint because step-down is not supported. `test_drain_insert_remove_within_same_transaction` directly creates insert/delete/update chains on a follower and verifies the promotion checkpoint completes without consecutive tombstone failure.

## Dependencies, Integration, Risks, And Test Signals
Integrates Oplog replay, layered ingest, stable timestamps, and role transitions. Risks are duplicate tombstones, incorrect operation ordering, inability to abandon leader-side post-checkpoint changes, and unverified post-step-down reopen paths. Signals are Oplog checks before and after checkpoint advance plus successful drain checkpoint; some later validation remains skipped pending WT-15763.
