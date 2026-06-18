# sources/storage-engines/foundationdb/bindings/java/src/integration/com/apple/foundationdb/RepeatableReadMultiThreadClientTest.java

## Purpose
This standalone multi-client workload attempts to verify repeatable-read semantics: long-running transactions should continue seeing the original value while separate transactions commit a new value and then read it.

## Important APIs, Types, and Functions
The file defines `RepeatableReadMultiThreadClientTest`, nested `OldValueReader`, nested `NewValueReader`, static configuration, and `setupThreads`, `setup`, `readOldValue`, and `setNewValueAndRead`. It uses `FDBOptions` for multi-client setup, `Database.run`, tuple encoding, and JUnit assertions from a main-driven workload.

## Control Flow
`main` configures external clients, opens databases from `FDB_CLUSTERS`, writes `foo=bar`, starts old-value reader threads, sleeps one second, starts new-value writer/reader threads, joins new readers, asserts old readers are still alive, then joins old readers. Old readers run one transaction that repeatedly reads the key with sleeps, expecting `bar`. New readers write `cool` in one transaction and read it in another.

## State and Persistence Behavior
The test writes un-namespaced key `foo` to each configured database and leaves it set to `cool`. Static `threadToOldValueReaders` records thread-to-reader state.

## Dependencies and Integration Points
It depends on multi-client external client configuration, tuple encoding, transaction snapshot behavior, and Java thread scheduling.

## Risks and Edge Cases
There is a likely test bug: `readOldValue` creates `oldValueReader`, but starts `new Thread(OldValueReader.create(db))`, then stores the unused `oldValueReader` in the map. The assertions inspect success flags on instances that never ran, so old-reader failures can be missed. Old readers also perform `Thread.sleep` inside a transaction, making the test timing-sensitive and potentially vulnerable to transaction timeout or retry behavior. It is not a JUnit `@Test`, so execution depends on an external runner invoking `main`.

## Test Signals
If corrected, passing would indicate repeatable-read snapshot semantics across concurrent multi-client transactions. As written, liveness checks still signal that old reader threads ran long enough, but success validation is weakened by the instance mismatch.
