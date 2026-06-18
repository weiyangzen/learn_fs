# sources/storage-engines/wiredtiger/test/suite/test_layered_prepare06.py

## Purpose

This broad suite tests layered cursor walking on a follower after checkpoint advancement, especially the two-cursor merge path between stable and ingest trees. It verifies correct scan position around overwrite updates, prepared conflicts, prepare commits, prepare rollbacks, boundary conflicts, and reverse iteration.

## Important APIs, Types, and Functions

Helpers include `early_setup` for follower storage links, `populate_leader_and_checkpoint`, `open_follower`, `walk_next_collect`, `walk_prev_collect`, `setup_committed_then_prepared`, `setup_prepared_rollback`, `commit_prepared`, and `rollback_prepared`. The class uses `preserve_prepared=true`, `precise_checkpoint=true`, `wiredtiger.WT_PREPARE_CONFLICT`, and `wiredtiger_strerror` for reliable conflict detection.

## Control Flow

The first test positions a follower cursor through `search`, performs an overwrite update, advances a checkpoint, and verifies `next()` only returns keys greater than the search key. The remaining tests build stable data on the leader and follower-ingest committed or prepared writes, then scan forward or backward until a prepare conflict. They resolve the prepare by commit or rollback and continue scanning on the same cursor, checking set coverage, no duplicates, and monotonic ordering. Cases cover conflicts at scan start, middle, end, ingest-only keys, rolled-back never-committed keys, and rolled-back overwrites that must reveal prior committed values.

## State, Persistence, and Dependencies

State crosses leader stable checkpoint data, follower ingest writes, prepared transactions at timestamp 50, read transactions at timestamp 60, and role-specific disaggregated connection state. Dependencies include `os`, `wiredtiger`, `wttest`, `helper_disagg`, and `wtscenario`.

## Risks and Test Signals

The risk is losing the merge cursor position when a conflict interrupts a scan, causing skipped odd stable-only keys, duplicate keys, out-of-order results, or disappearance of a rolled-back overwrite's base value. Strong signals include exact set equality with all expected keys, no repeated keys across scan segments, ascending/descending order checks, and direct verification that rolled-back overwrites expose `committed_3`.
