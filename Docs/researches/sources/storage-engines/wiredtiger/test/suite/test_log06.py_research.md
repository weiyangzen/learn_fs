# sources/storage-engines/wiredtiger/test/suite/test_log06.py

## Purpose
Reproduces partial log record recovery where a 128-byte aligned zero-length block contains non-zero bytes and must be truncated safely.

## APIs, Types, And Functions
Defines `test_log06` with scenarios for non-zero record length bytes and flag bytes. It uses `copy_wiredtiger_home`, appends raw blocks to all copied log files, opens the copied home through `setUpConnectionOpen`, and matches recovery notice text.

## Control Flow, State, And Persistence
Phase 1 writes `value_a` and checkpoints. Phase 2 writes `value_b` to the WAL without checkpointing. Phase 3 copies the home while open, appends the corrupt block to copied logs, and closes the original. Phase 4 opens the copy expecting recovery notices and truncation. Phase 5 verifies every key has `value_b`, proving WAL replay before the partial block succeeded.

## Dependencies, Integration, Risks, And Test Signals
Depends on log alignment, transaction sync method `none`, crash-copy semantics, and recovery validation. Risks are over-truncating valid log content or failing to detect holes. Signals are expected NOTICE patterns and all rows preserving the post-checkpoint value.
