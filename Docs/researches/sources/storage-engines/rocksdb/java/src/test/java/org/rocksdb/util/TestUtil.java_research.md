# sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/util/TestUtil.java

Purpose: Shared RocksJava test utilities for common options, random dummy data, and `ByteBuffer` extraction.

Important APIs/types/functions: `optionsForLogIterTest`, `defaultOptions`, `dummyString(int)`, `bufferBytes(ByteBuffer)`.

Control flow and state: options helpers create configured `Options` objects with create-if-missing, write buffer sizes, target file size, and WAL/log iteration settings. `dummyString` uses a static `Random` and an alphabet to build byte arrays. `bufferBytes` copies remaining bytes from a `ByteBuffer` using `mark`, `get`, and `reset` so the caller’s position is preserved.

State and persistence behavior: options influence DB files in consuming tests, but this helper persists nothing. The static `Random` is shared and unseeded.

Dependencies and integration points: used throughout RocksJava tests for consistent option defaults and byte buffer assertions.

Risks: callers own returned native `Options` and must close them. Shared random is not deterministic and not synchronized. `bufferBytes` requires mark/reset support, which standard heap/direct buffers have but custom buffers might not.

Test signals: helper only; correctness is exercised by dependent tests.
