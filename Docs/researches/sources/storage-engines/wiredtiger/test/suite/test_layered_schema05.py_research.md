# sources/storage-engines/wiredtiger/test/suite/test_layered_schema05.py

## Purpose

This test verifies that missing local stable files for layered tables are recreated correctly from disaggregated metadata on restart. It covers both empty and populated tables.

## Important APIs, Types, and Functions

The class starts as a follower with statistics, statistics logging, and `precise_checkpoint=true`. Scenarios cover `layered:` URIs and `table:` URIs configured as layered disaggregated tables. It uses `restart_without_local_files()` to simulate loss of local files after stepping up and checkpointing.

## Control Flow

The test creates an empty table and a filled table, writes one timestamped row to the filled table, advances stable to timestamp 10, reconfigures the connection from follower to leader, and checkpoints. It then restarts without local files. After restart, it opens the empty table and confirms it has zero rows, then opens the filled table and confirms key `a` reads value `b`.

## State, Persistence, and Dependencies

State is persisted through role transition, stable timestamp, checkpoint, disaggregated metadata, and restart with local files removed. Dependencies include `wiredtiger`, `wttest`, `helper_disagg`, `wtscenario`, and generated disaggregated storage scenarios.

## Risks and Test Signals

The risk is that layered schema recovery cannot recreate missing stable constituents, or recreates them without the right data. Signals cover both an empty table and a table with committed content, ensuring recovery handles table existence and data visibility.
