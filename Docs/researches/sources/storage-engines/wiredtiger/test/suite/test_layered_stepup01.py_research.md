# sources/storage-engines/wiredtiger/test/suite/test_layered_stepup01.py

## Purpose
Exercises a basic disaggregated role swap where a follower becomes leader and writes new layered-table content that must be visible on both old and new leaders.

## APIs, Types, And Functions
Defines `test_layered_stepup01` under `@disagg_test_class`. It uses `wiredtiger_open` to open a follower home, `Session.create`, cursor inserts, `Session.checkpoint`, `disagg_switch_follower_and_leader`, and `disagg_advance_checkpoint`.

## Control Flow, State, And Persistence
The original leader creates a layered table and inserts three key families per item, checkpoints, then the helper switches leader/follower roles. The old follower inserts another three key families, checkpoints, and advances the old leader to the new checkpoint. Persistence is validated by scanning both connections and expecting six entries per logical item.

## Dependencies, Integration, Risks, And Test Signals
Depends on the disaggregated test hook and statistics logging; the test returns early on Darwin. The risk covered is role-switch state loss or partial checkpoint propagation. The main signal is full row-count equality on both connections after role inversion and checkpoint advancement.
