# sources/storage-engines/foundationdb/fdbserver/workloads/Sideband.cpp

## Purpose
`SidebandWorkload` tests causal visibility when one client notifies another client through a sideband `RequestStream` after committing a key. The checker must be able to read the committed key after receiving the message.

## Important APIs, Types, And Functions
The file defines serializable `SidebandMessage` and `SidebandInterface`, then registers `SidebandWorkload`. Important methods are `persistInterface`, `fetchSideband`, `mutator`, and `checker`. It uses `RequestStream`, endpoint serialization via `BinaryWriter`/`BinaryReader`, native `Transaction`, and perf counters for messages and causal errors.

## Control Flow
Each client persists its sideband interface in `Sideband/Client/<clientId>`. The mutator fetches the next client's interface, periodically creates a random `Sideband/Message/<key>`, commits `deadbeef`, records the commit version, and sends the key/version to the other client. The checker waits on its own request stream and reads the corresponding key, emitting a causal consistency error if it is absent.

## State And Persistence Behavior
Interface endpoints and message keys are persisted in normal keyspace. Message keys are not cleaned up. The workload records when a random message key was unexpectedly already present and uses that read version as a conservative commit version.

## Dependencies And Integration Points
It integrates Flow request streams with database transaction causality, endpoint serialization, and multi-client workload setup. It relies on every client successfully persisting an interface before peers fetch it.

## Risks And Edge Cases
The workload assumes client IDs form a ring and that request stream delivery plus database commit visibility should be causally safe. Key collisions are tracked but rare. Client actor errors and consistency errors are checked only at the end of the timed run.

## Test Signals
`CausalConsistencyError` indicates a sideband notification was received before the committed key was readable. `TestFailure` is emitted for client actor errors or nonzero causal consistency errors. Metrics include messages, causal errors, and unexpectedly present keys.
