# sources/storage-engines/wiredtiger/test/suite/test_prepare31.py

## Purpose

Tests checkpoint selection for rolled-back prepared updates under preserve-prepared, based on stable timestamp relative to prepare and rollback timestamps.

## Important APIs, Control Flow, and State

The class inherits `test_prepare_preserve_prepare_base`, which enables precise checkpoint, preserve prepared, and statistics. Helpers set up committed initial data, create a prepared transaction over many keys with `prepared_id=1`, roll it back at a supplied rollback timestamp, and inspect `rec_time_window_prepared`. Three tests assert checkpoint skips aborted prepared updates when rollback timestamp is stable, skips when prepare timestamp is not stable, and writes the prepared update when prepare is stable but rollback is not.

## Dependencies, Risks, and Test Signals

Dependencies are `wiredtiger.stat.dsrc.rec_time_window_prepared`, `checkpoint_and_verify_stats`, timestamp helpers, and prepared IDs. The risk is checkpoint writing or skipping aborted prepared updates at the wrong stability boundary. Signals are targeted reconciliation statistics for each timestamp regime.
