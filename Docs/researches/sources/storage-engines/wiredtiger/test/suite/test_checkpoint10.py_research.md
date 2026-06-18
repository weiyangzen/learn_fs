# sources/storage-engines/wiredtiger/test/suite/test_checkpoint10.py

Purpose: tests reading checkpoints created while a large transaction commits concurrently, without timestamps. The checkpoint must show either the pre-transaction or post-transaction state, never a torn intermediate state.

Important APIs/types/functions: `checkpoint_thread`, `named_checkpoint_thread`, `stat.conn.checkpoint_state`, `timing_stress_for_test=[checkpoint_slow]`, `SimpleDataSet`, `make_scenarios`, and checkpoint cursor scans.

Control flow: write baseline `value_a` rows and checkpoint, start a second session transaction writing `value_b` over an overlapping or nonoverlapping range, start named or unnamed checkpoint in a background thread, wait until checkpoint state is active, commit the transaction, optionally reopen, then scan the checkpoint and compare observed value counts to one of two valid maps.

State/persistence behavior: stresses checkpoint snapshot consistency across file/table generations, named/unnamed checkpoints, logging/nonlogging, and precise/fuzzy modes.

Dependencies/integration: concurrency, checkpoint state stats, transaction commit racing with checkpoint, and checkpoint cursor visibility.

Risks/test signals: disabled crash/RTS crosscheck notes flakiness in generating inconsistent checkpoints. Active assertion only checks visible checkpoint state.
