# sources/storage-engines/wiredtiger/test/model/src/driver/kv_workload_runner_wt.cpp

Purpose: executes model workloads against a real WiredTiger home, including intentional crash/restart handling and disaggregated storage support.

Important APIs and functions: `session_context` owns a WT session and lazily opens per-table cursors. `run` creates shared memory for return codes/state, applies initial config operations before opening, then forks a child to run/resume workload. Parent detects intentional crashes via shared state and resumes after crash operations. `do_operation` overloads map operation variants to WiredTiger APIs: transactions, checkpoints, crash kill, table create, cursor search/insert/remove/truncate, timestamps, rollback_to_stable, restart, and config storage. `wiredtiger_open_nolock` composes base/disagg/override config, opens WT, picks up latest disagg checkpoint, steps up leader role, and sets stable/oldest timestamps. `remove_local_files` clears WT files for disaggregated starts.

Control flow and state: shared state records configs, table URIs for recovery, return codes, crash index, and exceptions. Locks protect connection, sessions, and table URI maps. Crashes use `SIGKILL` in the child to avoid core files.

Dependencies and integration: depends on WT public/internal APIs, POSIX fork/wait/signal/dir APIs, `shared_memory`, data conversion cursor helpers, and disagg utilities.

Risks and test signals: Unix process semantics are required. Shared-state size caps table URI count/length. Child exceptions are marshaled back as strings. `get` still ignores read value. Strong signals are correct resume after intentional crash and matching return codes/verification versus the model.
