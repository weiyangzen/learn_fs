# sources/storage-engines/wiredtiger/test/suite/test_prepare_hs03.py

Purpose: validates that prepared updates and history-store state remain recoverable through corruption, salvage, verify, checkpoint, and simulated crash/restart sequences.

Important APIs and types: `copy_wiredtiger_home`, `SimpleDataSet`, `wiredtiger.stat`, helper methods `corrupt_table`, `corrupt_salvage_verify`, `get_stat`, `check_data`, `get_timestamps`, and `prepare_updates`.

Control flow: committed large values are written at an early timestamp, stable/oldest are set, the table is deliberately corrupted and salvaged/verified, then multiple sessions prepare later updates. The test checks mid-timestamp reads still return committed values, closes prepared sessions to roll them back, checks again, repeats corruption/salvage/verify, checkpoints, copies to `RESTART`, reopens, and checks data again.

State and persistence behavior: the committed versions may live in the history store while prepared updates are unresolved. Rollback of prepared sessions must restore visibility of committed values even after salvage and restart.

Dependencies and integration points: history store statistics, salvage/verify, file copying, crash-style reopen, timestamp hooks, and variable key formats.

Risks: corruption/salvage may not recover every key, so `check_data` counts successfully found keys and asserts those have expected values. This makes the test robust to salvage loss but less exhaustive.

Test signals: `cache_write_hs` delta is nonnegative, every recovered key has the committed value, and salvage/verify/restart phases complete.
