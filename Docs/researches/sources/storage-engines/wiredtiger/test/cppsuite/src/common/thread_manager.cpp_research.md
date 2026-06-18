# sources/storage-engines/wiredtiger/test/cppsuite/src/common/thread_manager.cpp

Purpose: Implements ownership and joining of worker threads used by cppsuite components.

Important APIs/types/functions: destructor logs an error if a stored thread remains joinable, joins it, deletes all thread pointers, and clears the vector. `join` waits until each thread is joinable, logs trace messages while waiting, then joins.

Control flow: `join` must be called by owners during normal finish; destructor is a safety net.

State and persistence: owns heap-allocated `std::thread` pointers in memory only.

Dependencies/integration: used by `workload_manager` to fan out operation threads; logs via `logger`.

Risks and test signals: heap-allocated thread pointers require destructor discipline. Waiting for `joinable()` is unusual because a newly constructed `std::thread` is joinable immediately; a hang here would signal corrupted/null thread state. Destructor error log indicates lifecycle misuse.
