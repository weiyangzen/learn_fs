# sources/storage-engines/wiredtiger/test/suite/test_checkpoint16.py

Purpose: ensures a table that is clean when a later checkpoint is taken can still be read from that checkpoint.

Important APIs/types/functions: `SimpleDataSet`, `make_scenarios`, helper `large_updates`, helper `do_checkpoint`, checkpoint cursor reads, and named/unnamed plus precise/fuzzy scenarios.

Control flow: create two tables, set oldest/stable to 5, write `value_a` to both tables and checkpoint, write `value_b` only to table 2, take a named or unnamed second checkpoint, then open table 1 from the second checkpoint and verify all 1,000 rows still read `value_a`.

State/persistence behavior: table 1 is clean for the second checkpoint but must still be included/addressable in that checkpoint. The test guards against checkpoint metadata omitting clean handles needed for reads.

Dependencies/integration: checkpoint metadata over multiple tables, clean-table handling, row/column formats, and hook skips for storage modes without named checkpoints.

Risks/test signals: failure is inability to open/read table 1 from the second checkpoint or wrong row values/count.
