## sources/user-network-fs/gcsfuse/internal/gcsx/inactive_timeout_reader_test.go

Purpose: unit tests for `InactiveTimeoutReader` lifecycle, timeout closure, reconnection, and locking behavior.

Important APIs and fixtures: `InactiveTimeoutReaderTestSuite`, simulated clock, fake storage readers, mock bucket expectations, `setupReader`, and explicit suite teardown that closes remaining readers.

Control flow and behavior covered: initial `NewReaderWithReadHandle` error propagation, zero-timeout rejection, successful initial reads, no close before timeout threshold, `io.ReadFull` success, reconnect failure after timeout, reconnect success with expected offset and stored read handle, explicit close, active-to-inactive timeout transition, nil/non-nil `closeGCSReader`, and concurrent reads while timeout handling runs.

State/persistence signals: tests inspect internal `gcsReader`, `seen`, and `isActive` state, and verify that timeout closure captures the underlying reader’s read handle for the next connection. Reconnect request matching confirms range start advances by bytes already read.

Dependencies/integration: uses `clock.SimulatedClock`, `storage.TestifyMockBucket`, fake readers, `testify/suite`, and GCS request types.

Risks/test signals: tests make timing deterministic through simulated clock except for the race test, which exercises concurrency but cannot prove absence of every race without `go test -race`. They document that explicit close stops the monitor.
