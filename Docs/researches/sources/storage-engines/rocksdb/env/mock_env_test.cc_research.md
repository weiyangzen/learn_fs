# sources/storage-engines/rocksdb/env/mock_env_test.cc

## Purpose
`mock_env_test.cc` is the focused unit test for `MockEnv`. It validates two mock-environment behaviors: unsynced data corruption and fake sleep advancing emulated time.

## Important APIs and control flow
`MockEnvTest` owns a `MockEnv*` created from `Env::Default()` and deletes it in the fixture destructor. The `Corrupt` test writes a synced prefix and an unsynced suffix to `/dir/f`. It reads the prefix through `RandomAccessFile`, fsyncs the file, calls `MockEnv::CorruptBuffer()`, and verifies the synced prefix is unchanged. It then appends a second string, verifies it is readable, corrupts again, and asserts that the unsynced suffix differs.

The `FakeSleeping` test captures `GetCurrentTime()`, calls `SleepForMicroseconds(3 * 1000 * 1000)`, and checks that the apparent wall time advanced by 3 or 4 seconds.

## State, persistence, and integration
The tests rely on `MockEnv`'s in-memory state, `WritableFile` fsync forwarding to `MemFile::Fsync()`, `RandomAccessFile` reads into scratch memory, and `EmulatedSystemClock` behavior from `MockEnv::Create()`. They integrate with RocksDB's `testharness`, stack trace handler, and standard `ASSERT_OK`/`ASSERT_EQ` macros.

## Risks and test signals
The corruption test only verifies that corruption changes a suffix, not the exact corruption range, and it depends on a random mutation being different from the original bytes. The fake-sleep test tolerates one extra second for runtime delay but can still be sensitive if the emulated clock or real clock backing changes. Passing tests signal that `fsynced_bytes_` boundaries, `CorruptBuffer()`, file read/write wrappers, and fake sleep behavior remain compatible with legacy in-memory-env expectations.
