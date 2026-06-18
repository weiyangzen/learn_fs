# sources/storage-engines/foundationdb/layers/taskbucket/test.py

Purpose: This Python 2 script is an executable demonstration of TaskBucket and FutureBucket. It creates a small task graph that says hello to 20 names and then schedules a final completion task.

Important APIs and types: It imports `taskbucket`, `Subspace`, and `TaskTimedOutException`, creates `TaskDispatcher`, `TaskBucket`, and `FutureBucket`, and registers `say_hello`, `say_hello_to_everyone`, and `said_hello` task functions.

Control flow: The script clears the database, creates an `all_done` future, clears the task bucket, adds the root `say_hello_to_everyone` task, and attaches `said_hello` as a callback task. The root task creates 20 child futures/tasks and joins them into `done`; each child prints a greeting, sets its future, and finishes itself. The main loop repeatedly calls `do_one`, sleeping when no task is available, and catches timed-out tasks.

State and persistence behavior: It destructively clears the key range `""` to `"\xff"`, then persists task and future state under `backup-agent`. Task functions finish their own task records inside transactions.

Dependencies and integration points: It manipulates local bindings/layers import paths, uses FDB API version 200, and opens the default database. It demonstrates how TaskBucket composes with Future callbacks.

Risks: The loop structure has an unreachable `break` because the inner loop is infinite unless interrupted, and full database clearing is hazardous. It is a demo, not a deterministic test. Structured tests should assert that all child futures are set, the final task runs once, and no available or timeout records remain.
