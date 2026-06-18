# sources/storage-engines/sqlite/src/os_common.h

Purpose: provides macros and small helpers shared by platform-specific `os_*.c` files. It is intentionally not a general-purpose header.

Important macros and state: rejects obsolete `MEMORY_DEBUG`, defines optional `TIMER_START`, `TIMER_END`, and `TIMER_ELAPSED` for `SQLITE_PERFORMANCE_TRACE`, declares test globals for I/O errors and disk-full simulation, and defines `SimulateIOErrorBenign()`, `SimulateIOError()`, `SimulateDiskfullError()`, and `OpenCounter()`. `local_ioerr()` increments hit counters and hard-hit counters for non-benign faults.

Control flow: in test builds, the simulate macros inject caller-provided code when pending or persistent counters indicate an error should occur. In non-test builds, all simulation and open-counter macros compile away. Performance timers compile to hardware-time reads only when explicitly enabled.

State and persistence: test-only global counters are shared with `os.c`. They are transient process state used by regression tests, not persisted.

Dependencies and integration points: used by concrete VFS implementations such as Unix and Windows. It depends on `IOTRACE`, `sqlite3Hwtime()`, and the test globals defined in `os.c`. `OpenCounter()` lets VFS code update `sqlite3_open_file_count`.

Risks: simulation macros execute arbitrary caller code and must be placed only where the VFS can safely abort with the intended error. Non-test builds must stay side-effect-free. The obsolete macro check intentionally fails old build configurations.

Test signals: run `SQLITE_TEST` I/O error and disk-full suites; verify benign errors do not increment hard-hit count; build with `SQLITE_PERFORMANCE_TRACE`; and compile platform VFS files in non-test mode to ensure macros disappear cleanly.
