# sources/storage-engines/wiredtiger/test/cppsuite/src/component/workload_manager.cpp

Purpose: Populates the database and starts configured workload operation threads.

Important APIs/types/functions: constructor wires config, database operation implementation, timestamp manager, and database. `set_operation_tracker` attaches tracking. `run` builds `operation_configuration` objects for background compact, checkpoint, custom, insert, read, remove, and update; populates the database; creates barriers and `thread_worker` objects; and launches operation functions through `thread_manager`. `finish` calls each worker's `finish`, joins threads, and logs completion.

Control flow: unlike the base component, `run` does one-time population and thread launch, then returns while worker threads continue. The top-level test later calls `finish` to stop/join workers.

State and persistence: owns thread workers, thread manager, database operation pointer, database reference, timestamp/operation tracker pointers, and `_db_populated` flag. Workload operations persist actual database contents.

Dependencies/integration: depends on `operation_configuration`, `thread_worker`, `database_operation`, `connection_manager`, `barrier`, and logger.

Risks and test signals: `do_work` asserts false because this component should not use base run-loop semantics. Thread and config lifetimes are delicate: operation configs are deleted after worker construction, so workers must not retain raw config pointers beyond construction. Join success and worker finish are the key lifecycle signals.
