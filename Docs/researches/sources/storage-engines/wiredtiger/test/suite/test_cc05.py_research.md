# sources/storage-engines/wiredtiger/test/suite/test_cc05.py

Purpose: verifies checkpoint cleanup/garbage collection does not remove a checkpoint that is locked by an open checkpoint cursor. It covers named and unnamed checkpoint flows for column and integer row formats.

Important APIs/types/functions: inherits `test_cc_base`, `SimpleDataSet`, `make_scenarios`, `session.open_cursor(... checkpoint=...)`, `large_updates`, `check_cc_stats`, and skip for disaggregated storage.

Control flow: write values at timestamps 20, 30, 40, set stable to 35, create a named or unnamed checkpoint, open a cursor on it, advance oldest/stable to 40, write more generations at 50/60/70, advance oldest/stable to 70, force cleanup, and verify the open cursor still reads value at timestamp 30 (`value_y`). After closing, named checkpoints should still read `value_y`; unnamed latest checkpoint should read `value_w`.

State/persistence behavior: an open checkpoint cursor pins a checkpoint while cleanup removes older history. Named checkpoints persist by name; unnamed `WiredTigerCheckpoint` resolves to latest after cursor close.

Dependencies/integration: checkpoint cursor pinning, timestamp history, cleanup stats, and named checkpoint support.

Risks/test signals: failure indicates cleanup deleted in-use checkpoint state or named/unnamed checkpoint resolution regressed.
