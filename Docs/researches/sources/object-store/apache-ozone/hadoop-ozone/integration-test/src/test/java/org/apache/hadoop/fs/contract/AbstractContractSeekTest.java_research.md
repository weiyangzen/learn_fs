# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/fs/contract/AbstractContractSeekTest.java

Purpose: `AbstractContractSeekTest` validates seek, positioned read, EOF, closed-stream, negative offset, random read, and buffer-boundary behavior for filesystems declaring `SUPPORTS_SEEK`.

Important APIs/types/functions: extends `AbstractFSContractTestBase`; uses `FSDataInputStream`, `FileSystem`, `Path`, `EOFException`, `RandomUtils.secure()`, `ContractTestUtils.createFile`, `dataset`, `touch`, `verifyRead`, and `skip`. It sets `io.file.buffer.size` to 4096, creates a deterministic 1024-byte seek file and zero-byte file in `setup()`, and closes `instream` in `teardown()`.

Control flow: zero-byte tests verify seek to 0 and block reads return EOF. Closed-stream tests assert read operations fail and conditionally allow seek/available on closed streams based on contract flags. Negative and past-EOF seek tests distinguish strict EOF behavior from contract-permitted alternatives, then verify stream recovery. Basic seek and big-file tests read known byte values at specific offsets and ensure positioned `readFully` does not change current position. `testRandomSeeks` performs a contract-limited number of random seek/read verifications and logs the last sequence on failure. Positioned-readable tests validate `readFully` and `read(position, buffer, offset, length)` argument validation, EOF handling, zero-length reads, null buffer handling, and exact EOF behavior.

State and persistence behavior: persistent file content is deterministic (`offset => byte value`) so stream cursor and positioned-read behavior can be checked precisely. The key mutable state is the input stream position, which must not change for positioned reads.

Dependencies and integration points: gated by `SUPPORTS_SEEK` and sometimes `SUPPORTS_POSITIONED_READABLE`, `REJECTS_SEEK_PAST_EOF`, `SUPPORTS_SEEK_ON_CLOSED_FILE`, and `SUPPORTS_AVAILABLE_ON_CLOSED_FILE`.

Risks and test signals: catches buffering bugs, cursor mutation during positioned reads, wrong EOF return values, invalid-argument acceptance, negative seek mishandling, closed-stream leaks, and random seek data corruption. It does not benchmark performance.
