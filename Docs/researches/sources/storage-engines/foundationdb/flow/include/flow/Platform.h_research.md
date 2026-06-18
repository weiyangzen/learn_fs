<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/include/flow/Platform.h -->
# sources/storage-engines/foundationdb/flow/include/flow/Platform.h

Purpose: This header centralizes Flow's platform abstraction layer. It defines OS/compiler portability macros, thread entry points, timers, filesystem helpers, system statistics, atomics, byte-order helpers, dynamic library loading, crash handling, profiling hooks, DTrace probes, and low-level allocation utilities.

Important APIs and types: Key definitions include exit codes, `__unixish__`, `FLOW_THREAD_SAFE`, `force_inline`, recursive `CRITICAL_SECTION` aliases, thread macros and `startThread`/`waitThread`, `DiskStatistics`, `SystemStatistics`, `MachineRAMInfo`, `timer`, `timer_monotonic`, `timer_int`, file/path helpers, `platform::TmpFile`, memory and random helpers, `timestampCounter`, interlocked operations, endian conversion macros, dynamic library APIs, trace profiling counters, `criticalError`, `flushAndExit`, `platformInit`, crash-handler registration, and DTrace probe shims.

Control flow: Most functions are declarations implemented in platform-specific source files. Preprocessor branches select Windows, Linux, FreeBSD, Apple, aarch64, x86, and PowerPC behavior. When `FLOW_THREAD_SAFE` is false, Flow interlocked wrappers become plain non-atomic operations for network-thread-owned data; when true, they map to platform atomics.

State and persistence behavior: This file does not own persisted state, but many declarations affect persistent side effects: atomic file replacement, filesystem reads/writes, directory creation, environment knob discovery, trace profiling state, and crash handling. `SystemStatistics` and `DiskStatistics` are snapshots with mixed cumulative and delta semantics.

Dependencies and integration points: Almost every Flow component includes this header directly or indirectly. It feeds `SystemMonitor`, `Trace`, `ThreadPrimitives`, network timers, file trace writers, platform setup, and tests that need temporary files or process statistics.

Risks: Because the header gates platform behavior with macros, build drift on new compilers or OSes can break broad surfaces. Non-thread-safe Flow atomic wrappers are correct only under main-thread ownership assumptions. `exit` is banned via macro policy, forcing `_exit`, `criticalError`, or `flushAndExit`. Some path helpers deliberately do logical path cleanup without resolving symlinks, which callers must understand.

Test signals: Coverage should include platform-specific build tests, timer monotonicity, file/path helper edge cases, dynamic library load/unload, atomic wrapper behavior under configured thread mode, crash-handler registration smoke tests, temp-file lifetime, and system statistics on supported OSes.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/include/flow/Platform.h -->
