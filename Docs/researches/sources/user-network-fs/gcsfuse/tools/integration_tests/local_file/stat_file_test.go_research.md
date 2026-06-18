<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/local_file/stat_file_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/local_file/stat_file_test.go

## Purpose

This file tests stat and truncate semantics for unsynced local files, including lookup through the conflicting-file-name suffix used by gcsfuse internals.

## Important APIs, Types, and Functions

Tests use `operations.VerifyStatFile`, `WritingToLocalFileShouldNotWriteToGCS`, `CloseFileAndValidateContentFromGCS`, `os.Truncate`, and `inode.ConflictingFileNameSuffix`.

## Control Flow

`TestStatOnLocalFile` creates a local file, stats size zero and permissions, writes content, stats the updated local size, then closes and validates GCS content. `TestStatOnLocalFileWithConflictingFileNameSuffix` stats `filePath + inode.ConflictingFileNameSuffix` and expects it to resolve to the local file metadata. `TestTruncateLocalFileToSmallerSize` writes content, verifies full size, truncates to `SmallerSizeTruncate`, verifies the smaller size, and validates truncated GCS content after close.

## State and Persistence Behavior

Stat observes local unsynced metadata before GCS persistence. Truncation mutates local buffered content and only persists the shortened content on close.

## Dependencies and Integration Points

It depends on gcsfuse inode conflict naming behavior, shared local file helpers, and operation validators. It covers metadata surfaces used by editors and tools that stat before close.

## Risks and Test Signals

The conflict suffix behavior is internal and can change with inode implementation. Passing signals are correct local size/permission metadata, suffix lookup support, and exact truncated persisted bytes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/local_file/stat_file_test.go -->
