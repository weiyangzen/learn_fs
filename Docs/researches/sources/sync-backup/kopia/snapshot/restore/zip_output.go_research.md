# sources/sync-backup/kopia/snapshot/restore/zip_output.go

Purpose: `restore.Output` implementation that serializes restored files into a zip stream.

Important APIs/types/functions: `ZipOutput`, `Parallelizable`, `Close`, `WriteFile`, `CreateSymlink`, and `NewZipOutput`.

Control flow: zip output is serial. Directory begin/finish hooks are no-ops; zip entries are created for files when `WriteFile` opens the snapshot file, prepares a `zip.FileHeader` with method, modified time, and mode, then copies data. Symlink creation only logs that it is unimplemented.

State and persistence: writes to the provided `io.WriteCloser` through `archive/zip`; it does not mutate local filesystem state and reports no existing files.

Dependencies and integration points: used by restore archive export paths where `method` controls zip compression/storage.

Risks and test signals: symlinks are silently skipped except for debug logging, and empty directories are not emitted. Callers must close the output to finalize the central directory. Integration tests should inspect produced archives.
