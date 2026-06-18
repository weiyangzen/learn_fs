# sources/sync-backup/kopia/internal/connection/reconnector_test.go

Purpose: exercises `Reconnector` lifecycle, retry behavior, connection reuse, explicit close, and concurrent use with a fake connector.

Important APIs/types/functions: `fakeConnector`, `fakeConnection`, `TestConnection`, `UsingConnection`, `UsingConnectionNoResult`, and `errgroup.Group`.

Control flow: the test opens a first connection, forces a closed-connection callback error to trigger reconnect, verifies later calls reuse connection 2, nests a use inside another callback, explicitly closes, verifies a new connection 3, tests fatal open error propagation, tests retry after a classified open failure, and runs three parallel callbacks.

State and persistence behavior: fake connector tracks connection IDs via `atomic.Int32` and one-shot `nextError`. No durable state.

Dependencies/integration: uses `testlogging`, `testutil.EnsureType`, `errgroup`, `time.Sleep`, and `testify/require`.

Risks/test signals: the fake connection `isClosed` flag is not used by connector operations, so tests validate control flow rather than real I/O failure. Parallel assertions confirm shared connection reuse but not data-race safety of real connection implementations.
