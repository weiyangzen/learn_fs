<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/e2e_tests/truncate_test.go -->
# sources/user-network-fs/blobfuse2/test/e2e_tests/truncate_test.go

## Purpose
Additional truncation-focused end-to-end tests attached to `dataValidationTestSuite`.

## Important APIs, Types, and Functions
Tests include `TestShrinkExistingFile`, `TestExpandExistingFile`, `TestTruncateNonExistingFile`, `TestWriteBeforeTruncate`, `TestWriteAfterTruncate`, and `TestTruncateToZero`. They reuse helpers from `data_validation_test.go` to create local/remote files, truncate both, write at offsets, validate content, and clean up.

## Control Flow and State
Shrink and expand tests run multiple size pairs ranging from 512KiB to 10GiB boundaries. Each case creates matching local and mounted files, validates, truncates, validates again, and removes local/remote/cache paths.

## Dependencies and Integration Points
Depends on the data validation suite globals and setup. It is part of the same e2e package and only runs when `TestDataValidationTestSuite` runs.

## Risks and Edge Cases
Large 10GiB truncate cases can be expensive and storage-dependent. Because it shares the parent suite setup, skip conditions in `data_validation_test.go` also skip these tests. Local versus remote validation assumes local filesystem sparse/truncate behavior is the reference.

## Test Signals
Strong signal for truncate correctness across shrink, expand, missing file errors, write-before/after truncate, and zero-length truncation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/e2e_tests/truncate_test.go -->
