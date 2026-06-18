# sources/storage-engines/rocksdb/port/stack_trace.h

Purpose: declares RocksDB's optional stack trace and crash callback interface.

Important APIs/types/functions: `InstallStackTraceHandler`, `PrintStack`, `PrintAndFreeStack`, `SaveStack`, `CrashCallback`, and `RegisterCrashCallback`.

Control flow: header-only declarations; platform selection happens in `stack_trace.cc`. Callers install handlers once, optionally register a single callback, and can explicitly save/print stack frames.

State and persistence behavior: the header exposes no state, but the implementation stores one process-wide callback and heap-allocated saved stacks.

Dependencies and integration points: included by unit-test, benchmark, and diagnostic code needing stack traces. It is namespace-scoped under `ROCKSDB_NAMESPACE::port`.

Risks and test signals: callback contracts are strict because callbacks run during fatal signals. Tests should verify no-op behavior on unsupported platforms and that saved stacks are freed through the matching API.
