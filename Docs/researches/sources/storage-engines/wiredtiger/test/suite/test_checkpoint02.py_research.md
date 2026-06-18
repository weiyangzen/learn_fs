# sources/storage-engines/wiredtiger/test/suite/test_checkpoint02.py

Purpose: concurrency stress test that runs background checkpoints while multiple operation threads insert/update data.

Important APIs/types/functions: `queue.Queue`, `threading.Event`, `wtthread.checkpoint_thread`, `wtthread.op_thread`, `make_scenarios`, and precise/fuzzy checkpoint config.

Control flow: create a table, start a checkpoint thread, enqueue 50,000 inserts and periodic `b` operations, start 10 or 30 worker threads depending on dataset size, wait for queue completion, stop/join all threads, then scan the table and assert keys are sequential from 1 to `nops` with expected value.

State/persistence behavior: mutates one table while checkpoints run concurrently. The final scan validates no committed operation was lost or reordered in the durable/live view.

Dependencies/integration: thread helpers from `wtthread`, checkpoint precision modes, row/column key formats, and queue draining on exceptions.

Risks/test signals: timing/concurrency sensitive; final data assertion catches missing or out-of-order keys, while thread exceptions surface through the test harness.
