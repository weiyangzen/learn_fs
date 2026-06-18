# sources/test-tools/crashmonkey/test/user_tools/WorkloadTest.cpp

Purpose: gtests for `WriteData`, verifying deterministic byte placement for sub-4 KiB aligned and unaligned writes. It ensures holes before an offset are zero and written bytes match the shared test pattern.

Important APIs/types/functions: `WriteData`, `open`, `unlink`, `read`, `close`, `memcmp`, constants `kTestDataSize` and `kTestDataBlock`, and gtest assertions.

Control flow: each test opens/truncates a temporary `test_file`, unlinks it for cleanup, calls `WriteData` with a specific offset/size, reads the expected file span, checks EOF, validates zero-filled holes where expected, and compares written data to the deterministic block at the expected offset.

State/persistence behavior: creates an unlinked temporary file and writes data through `pwrite`; persistence beyond the open fd is not relevant. Dependencies/integration: tests the helper used by generated CrashMonkey workloads.

Risks/test signals: no tests cover writes larger than 4 KiB, exact 4 KiB boundary crossings, error returns, or `WriteDataMmap`. The read loop can spin if `read` returns 0 before expected bytes.
