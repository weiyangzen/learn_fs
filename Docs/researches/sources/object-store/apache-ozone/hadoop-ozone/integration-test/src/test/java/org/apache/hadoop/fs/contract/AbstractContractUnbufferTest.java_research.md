# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/fs/contract/AbstractContractUnbufferTest.java

Purpose: `AbstractContractUnbufferTest` validates `FSDataInputStream.unbuffer()` for filesystems declaring `SUPPORTS_UNBUFFER`. It ensures unbuffer can be called before reads, after reads, on empty files, after close, repeatedly, and between sequential reads without corrupting content or stream position.

Important APIs/types/functions: extends `AbstractFSContractTestBase`; uses `FSDataInputStream`, `Path`, `ContractTestUtils.createFile`, `dataset`, byte-array comparisons, and AssertJ. `setup()` creates `unbufferFile` with deterministic `TEST_FILE_LEN` bytes and stores the expected bytes in `fileBytes`.

Control flow: each test opens a stream and calls helper `unbuffer(FSDataInputStream)`, which records `getPos()`, invokes `stream.unbuffer()`, and asserts position is unchanged. Full-file and partial validation helpers read expected lengths and compare bytes against either the full dataset or a sliced range. Tests cover unbuffer before read, after full read, empty file, closed stream, multiple consecutive unbuffers, and alternating unbuffer/read phases across eighth, quarter, and half-file ranges.

State and persistence behavior: the file content is stable; mutable state is stream buffer resources and stream position. The contract is that dropping buffers must not change logical read position and must not make subsequent reads return wrong bytes.

Dependencies and integration points: depends on `SUPPORTS_UNBUFFER` and Hadoop's `CanUnbuffer` behavior exposed through `FSDataInputStream`. Concrete filesystems may release network buffers, native buffers, or cached ranges behind the same API.

Risks and test signals: catches position resets, data corruption after buffer release, non-idempotent unbuffer, exceptions on closed or empty streams, and partial-read boundary mistakes. It does not inspect actual resource reclamation.
