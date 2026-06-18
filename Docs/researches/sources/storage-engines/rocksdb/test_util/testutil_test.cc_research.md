# sources/storage-engines/rocksdb/test_util/testutil_test.cc

Purpose: provides a focused gtest for recursive directory destruction through the file utility layer.

Important APIs/control flow: helper `CreateFile()` opens a writable file with `Env::NewWritableFile()` and closes it. `TEST(TestUtil, DestroyDirRecursively)` creates a per-thread test directory with a file and nested directory/file, calls `DestroyDir(env, test_dir)`, then asserts the directory no longer exists. `main()` installs the stack-trace handler, initializes gtest, and runs all tests.

State behavior: creates and deletes files under the Env test directory. It expects a clean per-thread path and leaves no durable state on success.

Dependencies/integration: uses `testutil.h`, `file/file_util.h`, RocksDB Env APIs, gtest harness macros, and stack-trace installation.

Risks and test signals: the test is a smoke test for recursive deletion, not exhaustive coverage of permission errors, symlink behavior, or concurrent deletion. It assumes `CreateDir()` succeeds on a fresh path. Failure signals are direct `ASSERT_OK` or final `IsNotFound()` assertions.
