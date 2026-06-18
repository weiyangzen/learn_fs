# sources/sync-backup/restic/internal/fs/fs_reader.go

Purpose: Implements an in-memory/synthetic `FS` exposing a single reader as a file plus generated parent directories.

Important APIs: `ReaderOptions`, `NewReader`, `reader.OpenFile`, `Lstat`, path helpers, `readerFile`, `ErrFileEmpty`, `fakeFile`, and `fakeDir`.

Control flow and state: `NewReader` normalizes the target path, creates a file item and all ancestor directory items, and records child names. The file reader can be opened once using `sync.Once`; later opens return `EIO`. `readerFile.Read` turns EOF before any bytes into `ErrFileEmpty` unless empty files are allowed.

Dependencies and integration: Used for backup from stdin or command output as a virtual filesystem. Converts synthetic metadata to `data.Node` with current UID/GID.

Risks: Single-open semantics are strict and can surprise callers that retry reads. `fakeDir.Readdirnames(n>0)` is unimplemented. Path handling uses slash-based `path`, not OS-specific separators.

Test signals: `fs_reader_test.go` covers file content, nested directories, stat/lstat, missing paths, single synthetic directory traversal, and empty-reader errors.
