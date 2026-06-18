## sources/sync-backup/syncthing/lib/discover/mocks/manager.go

Purpose: Counterfeiter-generated fake for `discover.Manager`.

Important APIs/types/functions: Fake `Manager` implements `Cache`, `ChildErrors`, `Error`, `Lookup`, `Serve`, and `String`, with stubs, call counters, argument accessors, default/per-call returns, and `Invocations`.

Control flow: Each method records invocation under locks, copies mutable slice args where needed, calls a stub when configured, otherwise returns configured values.

State and persistence: In-memory fake state protected by per-method mutexes. No persistence.

Dependencies and integration points: Imports `discover` and `protocol`; compile-time assertion satisfies `discover.Manager`.

Risks: Generated code can drift from interface changes. Return maps/slices are not deep-copied, so tests can accidentally share mutable state.

Test signals: Compile-time conformance assertion is the main guard.
