# sources/storage-engines/wiredtiger/test/cppsuite/src/component/workload_manager.h

Purpose: Declares the component responsible for executing database workloads.

Important APIs/types/functions: `workload_manager` overrides `run`, `finish`, and `do_work`, exposes `get_database`, `db_populated`, and `set_operation_tracker`, and stores worker/thread orchestration state.

Control flow: top-level tests use it as the workload phase owner rather than a periodic component.

State and persistence: holds database reference, database operation pointer, timestamp manager pointer, operation tracker pointer, worker vector, thread manager, and population flag.

Dependencies/integration: includes configuration, database operation, thread worker, and thread manager.

Risks and test signals: destructor deletes workers but not the database operation or timestamp manager, so ownership is external for those pointers. Tests should verify `db_populated` before validation phases that assume existing data.
