# sources/storage-engines/wiredtiger/test/cppsuite/src/common/thread_manager.h

Purpose: Declares a simple thread owner for cppsuite workloads.

Important APIs/types/functions: `add_thread` templated helper allocates a `std::thread` with forwarded callable/args and stores it; `join` joins all workers; destructor cleans up.

Control flow: callers add all worker threads, later call `join`, then allow destruction.

State and persistence: stores `std::vector<std::thread *>`.

Dependencies/integration: used by components that need fan-out, especially workload execution.

Risks and test signals: raw pointer ownership increases leak/double-delete risk if future code mutates `_workers`; no API for clearing after join means destructor still deletes joined thread objects.
