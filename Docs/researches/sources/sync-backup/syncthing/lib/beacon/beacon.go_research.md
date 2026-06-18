# sources/sync-backup/syncthing/lib/beacon/beacon.go

Purpose: Shared supervisor-backed abstraction for UDP broadcast and multicast discovery beacons.

Important APIs/types/functions: `recv` pairs payload bytes with source address. `Interface` combines `suture.Service`, `fmt.Stringer`, `Send`, `Recv`, and `Error`. `cast` embeds a suture supervisor and owns reader/writer services plus inbox/outbox channels. `newCast`, `addReader`, `addWriter`, `createService`, `String`, `Send`, `Recv`, and `Error` implement common behavior.

Control flow: `newCast` creates a supervisor with debug logging and slow restart backoff, initializes channels, and closes `stopped` when the supervisor finishes. `Send` writes to the inbox unless stopped. `Recv` reads one message from the outbox or returns nils when stopped. `Error` reports reader error first, then writer error.

State and persistence behavior: In-memory channels and service error state only. No persistence.

Dependencies and integration points: Used by `NewBroadcast` and `NewMulticast`. Integrates with suture supervision and `svcutil.ServiceWithError`.

Risks: `Send` can block if the writer service is not draining inbox. `Recv` returns nil data/address on stop, so callers must handle that sentinel. Reader/writer errors depend on service wrapper semantics.

Test signals: Broadcast address calculation is tested in `broadcast_test.go`; cast orchestration is not directly tested here.
