# sources/test-tools/crashmonkey/test/user_tools/CmFsOpsTest.cpp

Purpose: gtest/gmock suite for `RecordCmFsOps`, validating that wrapped filesystem calls update fd/mmap maps and append correct `DiskMod` records. It uses fake and mock `FsFns` implementations to avoid real filesystem effects.

Important APIs/types/functions: `FakeFsFns`, `MockFsFns`, `TestCmFsOps`, `RecordCmFsOps`, `DiskMod`, `CmOpen`, `CmClose`, `CmWrite`, `CmCheckpoint`, `CmMsync`, `CmMmap`, parameterized write-size and mmap tests, and gmock `EXPECT_CALL`/`ON_CALL`.

Control flow: tests simulate open/create/truncate cases, close success/failure, zero-byte writes, checkpoint recording, msync at different mmap offsets/pointers, writes that do or do not extend file size, and mmap flag combinations that should or should not be tracked. Parameterized tests cover full and partial write sizes plus shared/private/anonymous mapping behavior.

State/persistence behavior: exercises in-memory `fd_map_`, `mmap_map_`, and `mods_`; fake `stat` sizes model file extension decisions. No durable files are created.

Dependencies/integration: validates the wrapper layer that generated workloads use to produce logical operation logs. Risks/test signals: rename, unlink/remove, fallocate, pwrite, fsync/fdatasync/sync/sync_file_range, and serialization paths have little or no coverage here; the fake `FnPathExists` returns `0` as false in all default cases.
