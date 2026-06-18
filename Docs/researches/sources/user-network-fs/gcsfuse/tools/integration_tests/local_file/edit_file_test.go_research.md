<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/local_file/edit_file_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/local_file/edit_file_test.go

## Purpose

This file verifies editing and appending behavior after a newly created local file has been synchronized to GCS. It ensures subsequent open/write/append operations update remote object content correctly on close.

## Important APIs, Types, and Functions

`TestEditsToNewlyCreatedFile` and `TestAppendsToNewlyCreatedFile` use `CreateLocalFileInTestDir`, `operations.WriteWithoutClose`, `CloseFileAndValidateContentFromGCS`, `operations.OpenFile`, `WriteAt`, and `os.OpenFile` with `os.O_RDWR|os.O_APPEND`.

## Control Flow

Both tests create a local file, write `FileContents` three times, close it, and validate the concatenated object in GCS. The edit test reopens the file, writes `newContent` at offset zero, closes, and expects the prefix to be replaced while the trailing two original chunks remain. The append test reopens with append mode, writes `appendedContent`, closes, and expects the original content plus appended bytes.

## State and Persistence Behavior

The file transitions from local-only state to synced GCS object state, then back to a locally modified open handle whose final content is persisted on close. Append mode depends on current file size being correctly observed from the synced object.

## Dependencies and Integration Points

It depends on the local-file suite globals and helper utilities. It exercises writeback/edit paths under all mount modes and write buffer configurations selected by `setup_test.go`.

## Risks and Test Signals

Potential risks are sparse/truncated writes, incorrect append offset, or stale cached size after first close. Passing signals are exact GCS contents after edit and append close.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/local_file/edit_file_test.go -->
