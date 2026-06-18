# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucStats.hh

Purpose: provides a tiny stats increment helper that hides whether the build has atomic operations or must serialize increments through a mutex.

Important APIs, types, and functions: macros `_statsADD` and `_statsINC` select `AtomicAdd`/`AtomicInc` when `HAVE_ATOMICS` is defined, otherwise lock `statsMutex`. `XrdOucStats::Bump()` overloads increment or add to `int` and `long long` counters.

Control flow: callers pass a counter reference to `Bump()`. The method expands to an atomic or lock-protected update and returns immediately.

State and persistence: the only object state is `statsMutex` for non-atomic builds. Counters are owned by callers and are in-memory only.

Dependencies and integration points: depends on `XrdSysAtomics.hh` and `XrdSysMutex` availability from that include path. It integrates with modules that keep simple process-local counters.

Risks and test signals: macro bodies are not wrapped in `do { } while (0)`, so unusual call contexts could surprise maintainers. Atomic semantics depend on the platform implementation. Tests should compile both atomic and non-atomic configurations and stress concurrent increments for lost updates.
