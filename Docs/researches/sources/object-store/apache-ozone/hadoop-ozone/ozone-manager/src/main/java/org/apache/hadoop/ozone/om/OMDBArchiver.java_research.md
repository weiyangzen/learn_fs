# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/OMDBArchiver.java

## Purpose
`OMDBArchiver` is a helper for OM DB checkpoint streaming. It lets servlet code collect files while holding the bootstrap lock by hardlinking them into a temporary directory, then write the actual tar archive later after the lock is released. It also records hardlink metadata so followers can reconstruct deduplicated checkpoint files.

## Important APIs, types, and functions
The class tracks `tmpDir`, a map from archive entry name to hardlink file, a map from absolute source path to file id, and a `completed` flag. `setTmpDir` must be called before file recording. `recordFileEntry(File, String)` creates or reuses a hardlink under `tmpDir` and records it for tar output. `recordHardLinkMapping` and `removeHardLinkMapping` maintain the metadata consumed by `writeHardlinkFile`. `writeToArchive(OzoneConfiguration, OutputStream)` writes the recorded files into a tar stream, deletes temporary hardlinks as they are consumed, and, when `completed` is true, appends the hardlink metadata file and Ratis snapshot completion marker.

## Control flow
During collection, callers set a temporary directory and call `recordFileEntry` for each file selected for transfer. The method resolves a link path from `tmpDir` and `entryName`, handles an existing link by reusing it if it already points to the same file or deleting it otherwise, creates a hardlink, stores it in `filesToWriteIntoTarball`, and returns the source file length. During streaming, `writeToArchive` opens a tar archive wrapper around the response output stream, includes each linked file using its recorded entry name, logs progress roughly every 30 seconds, and deletes the hardlink in a `finally` block. Completion-only metadata is emitted after regular files.

## State and persistence behavior
The helper does not write OM metadata tables. It creates filesystem hardlinks in a temporary directory and deletes them after archive inclusion. The hardlink mapping is in-memory until `writeToArchive` serializes it through `OMDBCheckpointServletInodeBasedXfer.writeHardlinkFile`. If streaming fails partway through a file, the hardlink is still deleted by the `finally` block, and the caller is responsible for cleaning the temporary directory.

## Dependencies and integration points
It integrates with `Archiver.tar`, `Archiver.includeFile`, `HddsServerUtil.includeRatisSnapshotCompleteFlag`, and the inode-based servlet's `writeHardlinkFile`. The helper is used by `OMDBCheckpointServletInodeBasedXfer` to decouple lock-protected file selection from slow HTTP output.

## Risks and edge cases
`recordFileEntry` requires `tmpDir`; missing setup throws `IllegalStateException`. Entry names are used as filenames inside `tmpDir`, so callers must provide collision-resistant names, typically inode-derived ids. Reusing an existing hardlink checks `Files.isSameFile`; if an old entry points elsewhere, it is deleted. `filesToWriteIntoTarball` is a regular `HashMap`, so archive order is not stable and the class is not thread-safe. A failed archive write can leave some unprocessed hardlinks until outer cleanup removes the temp directory.

## Test signals
Tests should cover missing `tmpDir`, hardlink creation, reuse of an existing same-file link, replacement of a stale link, deletion after archive writing, completion marker emission only when `completed` is true, and hardlink metadata generation when mappings exist.
