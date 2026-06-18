# sources/storage-engines/wiredtiger/test/suite/test_layered_stepup06.py

## Purpose
Regression test for step-up when two prepared sessions share one `prepared_id`, including a write-free prepared session and a writing prepared session.

## APIs, Types, And Functions
Defines `test_layered_stepup06`, skipped for the tiered hook and decorated for disaggregated storage. It uses `preserve_prepared=true`, `prepare_transaction(prepared_id=42)`, role reconfiguration, timestamped commit or rollback, and read-timestamp verification.

## Control Flow, State, And Persistence
The leader commits base keys and checkpoints, then closes without a final checkpoint. A follower opens from checkpoint metadata, starts `top_session` with no writes and `work_session` with keys 4 through 6, both prepared under the same ID. The follower steps up to leader, resolves both sessions, checkpoints, and checks base plus prepared-key visibility.

## Dependencies, Integration, Risks, And Test Signals
Exercises prepared transaction tracking across sessions during disaggregated promotion. The failure class is resolving only the first prepared session for an ID, leaving writes conflicted or uncommitted. Test signals are successful step-up, successful resolution of both sessions, and read timestamp checks for commit versus rollback.
