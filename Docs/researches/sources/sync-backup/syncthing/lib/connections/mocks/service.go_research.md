## sources/sync-backup/syncthing/lib/connections/mocks/service.go

Purpose: Counterfeiter-generated fake for the `connections.Service` interface.

Important APIs/types/functions: `Service` fake implements `AllAddresses`, `ExternalAddresses`, `ListenerStatus`, `ConnectionStatus`, `NATType`, and `Serve`, plus call counters, argument capture, default returns, per-call returns, stubs, and `Invocations`.

Control flow: Each fake method locks its method mutex, records invocation metadata, snapshots the stub/default return, unlocks, then either invokes the stub or returns configured values.

State and persistence: Maintains in-memory call slices, return structs, per-call maps, and invocation maps protected by mutexes. No persistence.

Dependencies and integration points: Imports `connections` for status entry types and satisfies `connections.Service`; imports `context` for `Serve`.

Risks: Generated fakes can drift if the source interface changes and `go generate` is not rerun. `Invocations` shallow-copies slices and interface values, so tests should avoid mutating captured mutable return data.

Test signals: Compile-time assertion `var _ connections.Service = new(Service)` detects interface drift at build time.
