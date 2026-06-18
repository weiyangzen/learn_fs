## sources/sync-backup/kopia/fs/virtualfs/virtualfs_test.go

Purpose: verifies in-memory virtual filesystem wrappers.

Important APIs/types/functions: `TestStreamingFile`, `TestStreamingFileModTime`, `TestStreamingFileGetReader`, `TestStreamingDirectory`, `TestStreamingDirectory_MultipleIterationsFails`, and `TestStreamingDirectory_ReturnsCallbackError`.

Control flow, state, and persistence: tests pipe or byte-reader content into streaming files/directories, fetch entries through `fs` helpers, read data, and assert one-shot reuse errors. State is in-memory only.

Dependencies and integration points: validates `virtualfs` through public `fs` helpers and `testlogging`.

Risks and test signals: strong coverage for reader consumption and directory iterator consumption. Tests do not stress concurrent calls to `GetReader`, matching the implementation’s caller-safety note.
