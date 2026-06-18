# sources/user-network-fs/gcsfuse/tools/integration_tests/streaming_writes/symlink_file_test.go

## Purpose

Tests symlink behavior for files with in-flight streaming writes. It verifies reads through a symlink see unflushed local data and that deleting the target local file invalidates the symlink without uploading data.

## Important APIs, control flow, and dependencies

`TestCreateSymlinkForLocalFileAndReadFromSymlink` creates a symlink to the active file, writes data, validates `readlink`, opens the symlink, reads through it, and validates GCS content after close. `TestReadingFromSymlinkForDeletedLocalFile` follows the same setup, deletes the target file path, closes the original file handle without error, confirms no GCS object exists, and expects `os.Stat` on the symlink to fail.

## State, persistence, dependencies, and integration points

The tests combine symlink namespace entries with streaming buffer state. Reads through the symlink must resolve to the same open file data even before upload, while removing the target must prevent close from resurrecting the object.

## Risks and test signals

Risks include dereferencing symlinks through stale metadata, leaking content to GCS after target deletion, and inconsistent behavior between local and empty-GCS suite variants. Signals are successful `VerifyReadLink`, exact symlink readback, final content validation for the live-target case, object-not-found for the deleted-target case, and stat failure for the dangling link.
