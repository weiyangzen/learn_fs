# sources/storage-engines/wiredtiger/test/suite/test_layered_stepup03.py

## Purpose
Regression test for leader-to-follower transition while eviction may encounter pages with pending split state produced by a checkpoint.

## APIs, Types, And Functions
Defines `test_layered_stepup03`, mixing in `eviction_util`. It uses `populate`, `Connection.set_timestamp`, `Session.checkpoint`, `Connection.reconfigure` for aggressive eviction and role transition, `disagg_get_complete_checkpoint_meta`, `close_conn`, and `open_conn`.

## Control Flow, State, And Persistence
The test writes 10,000 1KB rows into a 10MB cache, sets stable timestamp, checkpoints to create clean pages that may carry split metadata, makes eviction aggressive, captures checkpoint metadata, reconfigures the active connection from leader to follower, waits briefly, then reopens as follower with the checkpoint. The persisted checkpoint must remain readable after concurrent eviction/role-change pressure.

## Dependencies, Integration, Risks, And Test Signals
Depends on layered block manager `block_manager=disagg`, eviction utilities, and disaggregated checkpoint metadata. Risks include assertion failures or corrupt page state when eviction sees split pages during role transition. The final signal is a full cursor scan count equal to the inserted row count.
