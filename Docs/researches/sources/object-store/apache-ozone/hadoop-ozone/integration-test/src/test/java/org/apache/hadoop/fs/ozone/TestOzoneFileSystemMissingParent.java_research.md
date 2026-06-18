# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/fs/ozone/TestOzoneFileSystemMissingParent.java

Purpose: tests OFS commit failure behavior when an open file's parent directory is removed or renamed before stream close.

Important APIs/types/functions: setup creates a volume/bucket and opens rooted OFS. `testCloseFileWithDeletedParent` creates `/volume/bucket/parent/file`, deletes `parent`, and expects close to fail. `testCloseFileWithRenamedParent` renames the parent to `parent1` before close and expects the same failure.

Control flow: create a file stream, mutate parent directory while stream remains open, then call `stream.close` inside `assertThrows(OMException.class)` and verify message text.

State and persistence behavior: file creation initially materializes the missing parent. If that parent disappears before commit, OM must not commit the child file; it reports that the parent directory does not exist.

Dependencies and integration points: uses OFS URI, `FSDataOutputStream`, `FileSystem.delete`, `FileSystem.rename`, and OM exception reporting. Per-test cleanup recursively deletes the bucket path.

Risks: stream close error text is asserted literally enough to catch message changes. Open stream resources are intentionally not closed successfully after failure.

Test signals: detects stale-parent validation gaps that could commit files into deleted or renamed directories.
