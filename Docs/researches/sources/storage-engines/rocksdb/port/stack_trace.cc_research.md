# sources/storage-engines/rocksdb/port/stack_trace.cc

Purpose: implements RocksDB stack-trace capture and signal handling for supported POSIX/Mac builds, with no-op fallbacks for unsupported platforms such as Windows, Cygwin, and Solaris.

Important APIs/types/functions: `InstallStackTraceHandler`, `PrintStack`, `SaveStack`, `PrintAndFreeStack`, and `RegisterCrashCallback`. Internals include `GetExecutableName`, `PrintStackTraceLine`, `GetLldbScriptSelectThread`, `StackTraceHandler`, `TerminationHandler`, and `AtExit`.

Control flow: if stack tracing is disabled at compile time, exported functions return immediately. Otherwise `InstallStackTraceHandler` installs handlers for crash signals, ignores `SIGPIPE`, registers lightweight termination handlers, and relaxes ptrace restrictions where supported. `PrintStack` prefers LLDB/GDB depending on environment variables, forks a child debugger, waits for success, then falls back to `backtrace` plus `addr2line`/`atos`.

State and persistence behavior: global atomics track the thread currently handling a trace, whether exit has begun, and the crash callback. `SaveStack` mallocs a callstack that must be freed by `PrintAndFreeStack`. No persistent files are written.

Dependencies and integration points: used by tests, benchmarks, and debugging binaries that opt into stack traces. It depends on `execinfo`, `pthread`, `fork`, debugger executables, `/proc` or `sysctl`, `port/lang.h`, and process signal semantics.

Risks and test signals: signal handlers call non-async-signal-safe routines by design, so recursion/race handling is defensive but imperfect. Debugger invocation can hang or fail under ptrace restrictions. Environment variables `ROCKSDB_NO_STACK`, `ROCKSDB_DEBUG`, `ROCKSDB_LLDB_STACK`, `ROCKSDB_GDB_STACK`, and `ROCKSDB_BACKTRACE_STACK` should be covered by crash/debug tests.
