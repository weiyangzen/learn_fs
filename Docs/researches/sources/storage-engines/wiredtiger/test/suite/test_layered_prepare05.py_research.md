# sources/storage-engines/wiredtiger/test/suite/test_layered_prepare05.py

## Purpose

This test checks reconciliation of rolled-back prepared updates in layered tables. It ensures the old committed value or deletion state is written correctly after a prepared update, reinsert, or remove is rolled back, across full-image and page-delta checkpoint modes.

## Important APIs, Types, and Functions

The test class extends `prepare_util.test_prepare_preserve_prepare_base`, inheriting `checkpoint_and_verify_stats`. Scenarios vary forced eviction and page delta support. `conn_config` disables internal and leaf page deltas when the `delta` scenario is false. The tested statistics are `rec_time_window_prepared`, `rec_page_delta_leaf`, and `rec_page_full_image_leaf`.

## Control Flow

Each test seeds keys 1-19, advances stable, checkpoints, optionally evicts the page, then opens a separate session to prepare and roll back a change to key 19. It first verifies that checkpointing before the prepare timestamp skips or minimally writes the page. It then advances stable to the prepare timestamp and expects a prepared time window to be reconciled. Finally it advances stable to the rollback timestamp and expects the committed base state to be written, then verifies the key's final value or absence.

## State, Persistence, and Dependencies

The tests are timestamp-heavy: committed timestamps 21/22, stable timestamps 20/21/30/35/45, prepare timestamp 35, and rollback timestamp 45. They depend on `wiredtiger`, `wttest`, `helper_disagg`, `prepare_util`, and `wtscenario`, and integrate with layered reconciliation, eviction, page deltas, durable tombstones, and preserve-prepare-base behavior.

## Risks and Test Signals

The risk is losing the pre-prepare base when a prepared update rolls back, especially after eviction or when a removed key is reinserted. Statistics verify whether a checkpoint actually wrote a prepared time window or page image/delta, and final cursor checks verify user-visible state. The reinsert case documents an expected extra write when eviction removed the prior tombstone from memory.
