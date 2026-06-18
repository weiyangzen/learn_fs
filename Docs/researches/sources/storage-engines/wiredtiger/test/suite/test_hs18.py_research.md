# sources/storage-engines/wiredtiger/test/suite/test_hs18.py

## Purpose

Comprehensive older-reader regression suite for interactions between timestamped updates, no-timestamp updates, modifies, tombstones, history-store eviction, and snapshot readers.

## Important APIs, Types, and Functions

Defines helpers `create_key`, `check_value`, `update_kv`, `start_txn`, and `evict_key`. Test methods cover a base scenario, read timestamp behavior, tombstone ignoring, multiple older readers, multiple missing timestamps, and modifies.

## Control Flow

Each method creates one-key version chains, starts long-running transactions at carefully chosen points, evicts pages with debug cursors, applies no-timestamp and timestamped updates/modifies, then verifies old cursors still read their expected versions. The modifies case also checkpoints to update internal last-running state before eviction.

## State and Persistence Behavior

State includes several concurrent sessions with pinned snapshots, HS entries created by eviction, no-timestamp globally visible updates, timestamped updates, tombstones, and reverse modifies.

## Dependencies and Integration Points

Depends on `wiredtiger.Modify`, `wttest`, scenario generation, multiple sessions, timestamped reads, and debug eviction.

## Risks and Maintenance Signals

The tests are intricate and rely on exact snapshot timing. Some comments acknowledge changed visibility for timestamp readers after eviction, so expectations encode nuanced internal behavior.

## Test Signals

Signals are exact per-session values before and after eviction across older readers, timestamp readers, missing timestamp chains, tombstone handling, and modify reconstruction.
