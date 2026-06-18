# sources/sync-backup/restic/internal/fs/fs_reader_test.go

Purpose: Unit tests for the synthetic reader filesystem.

Important APIs: Helpers `verifyFileContentOpenFile`, `verifyDirectoryContents`, `checkFileInfo`, `createReadDirTest`, `createFileTest`, `createDirTest`, and tests `TestFSReader`, `TestFSReaderNested`, `TestFSReaderDir`, `TestFSReaderMinFileSize`.

Control flow and state: Each subtest builds a fresh `NewReader` because file content is single-use. Tests compare directory entries, content bytes, missing-path errors, metadata, absolute/relative cleaning, and empty-reader behavior.

Dependencies and integration: Covers `FS` contract compliance for `reader`, `readerFile`, `fakeFile`, and `fakeDir`.

Risks: Does not directly test second-open `EIO`; focuses on normal backup-like access.

Test signals: Good behavioral coverage for stdin/command backup filesystem semantics.
