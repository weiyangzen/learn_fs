# sources/test-tools/crashmonkey/test/harness/TesterTest.cpp

Purpose: gtest for `Tester::log_snapshot_save`. It verifies that a synthetic device snapshot is written byte-for-byte to a file.

Important APIs/types/functions: `TestTester`, `log_snapshot_save`, `mkstemp`, `ifstream`, `std::equal`, and `SUCCESS`. The test uses an 8 KiB buffer filled with byte value 42.

Control flow: create temp file, fill snapshot buffer, install it into `TestTester`, call `log_snapshot_save`, read the file back, assert EOF and byte equality.

State/persistence behavior: writes a temporary snapshot file under `/tmp`; no cleanup is performed after reading. Dependencies/integration: links `Tester.cpp`, utils, gtest/gmock, and `-ldl`.

Risks/test signals: passes stack memory to a helper that may delete previous/owned snapshots, and it does not unlink the temp file. The core signal is file content equality and `SUCCESS` return.
