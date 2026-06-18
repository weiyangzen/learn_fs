# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/connection/SequenceWindow.java

Purpose: `SequenceWindow` manages SMB message IDs and credits.

Important APIs and control flow: starts with one available permit and lowest ID zero. `get()` or `get(credits)` waits up to five seconds for permits, then returns a consecutive range and increments `lowestAvailable`. `creditsGranted` releases permits. `disableCredits` swaps in a semaphore that never blocks.

State, dependencies, and integration: `Connection.send` consumes sequence numbers and credit grants; packet handlers add credits from responses.

Risks: timeout and permit math directly affect throughput and deadlock behavior. `disableCredits` is a test/protocol escape hatch. Tests should cover initial ID zero, consecutive ranges, timeout failure, interrupted waits, credit grants, and no-op semaphore behavior.
