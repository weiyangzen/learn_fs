# sources/storage-engines/wiredtiger/test/suite/test_layered_stepup02.py

## Purpose
Verifies that layered tables can accept inserts under both initial leader and follower roles, and that a leader can reopen as follower in the same home while preserving data.

## APIs, Types, And Functions
Defines `test_layered_stepup02` with `conn_config()` returning `disaggregated=(role="<initial_role>")`. It uses `SimpleDataSet.populate`, `SimpleDataSet.check`, `Session.checkpoint`, `reopen_conn`, and `disagg_get_complete_checkpoint_meta`.

## Control Flow, State, And Persistence
Each scenario starts as either leader or follower, populates 1000 rows, and checks them. In the leader scenario, it checkpoints, reopens the same directory as follower with captured checkpoint metadata, appends another 1000 rows, and checks the expanded dataset. The persisted state is the disaggregated checkpoint metadata plus local table content across connection reopen.

## Dependencies, Integration, Risks, And Test Signals
Integrates `wtdataset.SimpleDataSet`, role scenarios, and disaggregated storage scenarios. It mainly protects against role-specific insert restrictions and incorrect checkpoint metadata reuse during same-home role changes. Test signals are `SimpleDataSet.check()` before and after reopen.
