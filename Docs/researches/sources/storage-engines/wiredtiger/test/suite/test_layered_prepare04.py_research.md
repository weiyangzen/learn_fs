# sources/storage-engines/wiredtiger/test/suite/test_layered_prepare04.py

## Purpose

This suite tests layered ingest garbage collection around prepared and aborted prepared updates. It ensures prepared updates and rollback records are retained until their prepare or rollback timestamps are safely covered by the checkpoint timestamp, and then become collectible at the correct time.

## Important APIs, Types, and Functions

The class runs both `layered:` and `table:` layered creation forms over disaggregated storage scenarios. Connections enable `statistics=(all),precise_checkpoint=true,preserve_prepared=true`. `create_follower` opens a follower; each test manually mirrors leader writes into follower ingest. Assertions read data-source statistics including `rec_ingest_garbage_collection_keys_update_chain`, `rec_ingest_garbage_collection_keys_disk_image`, and `rec_ingest_keep_prepare_rollback`.

## Control Flow

The tests create committed baseline records, introduce prepared inserts or updates, sometimes roll them back at timestamp 30, move stable timestamps in phases, checkpoint the leader, advance the follower checkpoint, force follower eviction, and inspect reconciliation counters. Cases include a live prepared insert, rolled-back prepared insert, live prepared update, rolled-back prepared update, and obsolete rolled-back prepared insert later superseded by a committed update.

## State, Persistence, and Dependencies

Persistent behavior is observed through checkpointed stable tables, follower ingest updates, rollback timestamps, oldest/stable timestamp movement, and eviction-triggered reconciliation. Dependencies include `wiredtiger`, `wttest`, `helper_disagg`, `wtscenario`, and `wiredtiger.stat`.

## Risks and Test Signals

The main risk is over-aggressive GC that removes a prepared cell or prepare rollback before it is globally safe, or under-aggressive GC that retains obsolete entries after all relevant timestamps are stable. Statistics assertions give precise signals about whether GC came from update chains or disk images and whether prepare rollback retention was counted. The phased timestamp movement makes regressions visible at the exact transition points.
