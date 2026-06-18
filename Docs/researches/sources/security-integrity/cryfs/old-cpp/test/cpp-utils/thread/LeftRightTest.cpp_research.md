# sources/security-integrity/cryfs/old-cpp/test/cpp-utils/thread/LeftRightTest.cpp

Purpose: Tests the `LeftRight` concurrency helper, which allows reads and writes with a double-buffer-like synchronization model. It covers integer/vector state, return values, concurrent reads, read/write concurrency, write exclusion, and exception safety.

Important APIs and types: Uses `cpp-utils/thread/LeftRight.h`, GoogleTest, vectors, local `MyException`, and threaded reader/writer lambdas.

Control flow: Tests perform read and write transactions, run concurrent readers/writers, and deliberately throw exceptions inside read or write callbacks to verify propagation and state recovery.

State and persistence behavior: State is in-memory protected data. Write exception tests validate whether old state is restored or new state kept depending on which phase fails.

Dependencies and integration points: Useful for thread-safe shared state with high read concurrency.

Risks: Concurrency tests can be timing-sensitive and may not exhaustively expose races. Exception-safety behavior is subtle and compatibility-sensitive.

Test signals: Correct visible state after writes, concurrent reads allowed, writes serialized, reads concurrent with writes as designed, returned values, propagated exceptions, and state rollback/commit semantics.
