<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/ProtocolVersion.cpp -->
# sources/storage-engines/foundationdb/flow/ProtocolVersion.cpp
- Purpose: Owns the mutable process-wide current protocol version used by Flow serialization and compatibility checks.
- Important APIs/types/functions: `currentProtocolVersion()` returns `g_currentProtocolVersion`; `useFutureProtocolVersion()` switches it to `futureProtocolVersionValue`.
- Control flow: The first call to `currentProtocolVersion()` captures a static copy of the current value and asserts on every later call that the global has not changed. Tests that need the future version must call `useFutureProtocolVersion()` before any normal protocol-version access.
- State and persistence behavior: The only state is the anonymous-namespace `g_currentProtocolVersion`. It is process-local and not persisted. The static guard inside `currentProtocolVersion()` makes late mutation an assertion failure.
- Dependencies and integration points: Depends on generated `flow/ProtocolVersion.h` constants and on Flow assertions. It is used wherever network protocol, object serializer, or persisted key format behavior gates on protocol version.
- Risks: Ordering is subtle; a test or bootstrap path that calls `currentProtocolVersion()` too early prevents later future-version testing. The global is not synchronized, so mutation is expected only during single-threaded setup.
- Test signals: Coverage should include default value reads, future override before first read, and assertion behavior for an attempted late override in debug/simulation contexts.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/ProtocolVersion.cpp -->
