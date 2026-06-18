<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/local_file/write_file_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/local_file/write_file_test.go

## Purpose

This file tests write ordering semantics for newly created local files, including sequential writes, random overwrites, out-of-order writes, sparse writes, and writes starting at non-zero offsets.

## Important APIs, Types, and Functions

Tests use `CreateLocalFileInTestDir`, `operations.WriteWithoutClose`, `operations.WriteAt`, `ValidateObjectNotFoundErrOnGCS`, and `CloseFileAndValidateContentFromGCS`.

## Control Flow

`TestMultipleWritesToLocalFile` writes `FileContents` three times and verifies no pre-close GCS object. `TestRandomWritesToLocalFile` writes overlapping strings at offsets 0, 2, and 3, expecting final content `stsstring3`. `TestOutOfOrderWritesToNewFile` writes two chunks then overwrites offset zero with `hello`. `TestMultipleOutOfOrderWritesToNewFile` writes at offsets 15 and 30, expecting zero-filled sparse bytes between. `TestWritesToNewFileStartingAtNonZeroOffset` writes at offset 15 before offset zero, expecting zero fill.

## State and Persistence Behavior

The local write buffer must support overwrite and sparse regions before upload. GCS persistence happens only at close and should reflect the final byte layout, including zero-filled gaps.

## Dependencies and Integration Points

It depends on local helper state and operation write helpers. It exercises local-file writeback buffering under the package's write-block-size and max-block flag variants.

## Risks and Test Signals

Expected strings encode exact sparse-byte behavior. Passing signals are absent pre-close objects and exact final GCS bytes for sequential, overlapping, out-of-order, and sparse writes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/local_file/write_file_test.go -->
