<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/e2e_tests/data_validation_test.go -->
# sources/user-network-fs/blobfuse2/test/e2e_tests/data_validation_test.go

## Purpose
End-to-end data integrity suite comparing local filesystem behavior with Blobfuse2-mounted paths across small, medium, large, huge, sparse, random-write, and panic-regression scenarios.

## Important APIs, Types, and Functions
Defines flags for mount path, temp/cache path, ADLS mode, quick mode, stream-direct mode, distro, and block size. `dataValidationTestSuite` provides helpers for cleanup, copying, MD5 computation, content validation, file creation, truncation, writes, sparse writes, random file generation, and local/remote path conversion. Tests include overwrite via shell, small/medium/large data copy validation, negative diff validation, multi-file concurrent validation, sparse/random writes, byte-count reads across block boundaries, and panic regressions around close/write/read paths.

## Control Flow and State
`TestDataValidationTestSuite` initializes buffers, skips non-Ubuntu or quick mode, creates a random test directory under the mount, sets local and cache paths, fills random buffers, runs the suite, and removes the mount test directory. Individual tests write both local and mounted files, compare size and MD5, and often clear cache paths to force Blobfuse2 re-read behavior.

## Dependencies and Integration Points
Depends on a live Blobfuse2 mount, local filesystem, cache directory, Linux commands `cp` and `diff`, `testify/suite`, and Go crypto/rand/md5. It integrates with block-cache behavior via `block-size-mb` and stream-direct skip logic.

## Risks and Edge Cases
The suite allocates up to hundreds of MiB and can create 10GiB sparse/truncated files. It is environment-gated and skipped in quick/non-Ubuntu modes, so coverage can be absent in many CI runs. Some helpers use package globals (`tObj`, buffers), limiting parallel safety. Cache deletion during mounted operation can expose timing/flakiness.

## Test Signals
Strong signal for data integrity: MD5 equality against local files, exact size checks, EOF byte counts, expected diff failure in negative test, and absence of panics in block-cache regression cases.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/e2e_tests/data_validation_test.go -->
