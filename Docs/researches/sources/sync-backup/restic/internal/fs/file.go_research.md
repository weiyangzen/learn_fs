# sources/sync-backup/restic/internal/fs/file.go

Purpose: Package-level filesystem helpers that wrap standard `os` operations with platform path normalization.

Important APIs: `MkdirAll`, `Remove`, `RemoveAll`, `Link`, `Lstat`, `OpenFile`, `IsAccessDenied`, `ResetPermissions`, and `Readdirnames`.

Control flow and state: Most functions call `fixpath` then `os` equivalents. `Readdirnames` opens a directory through an `FS` with `O_RDONLY|O_DIRECTORY|flags`, reads all names, closes the file, and preserves close/read errors carefully.

Dependencies and integration: Used across restore and backup paths where long Windows paths or VSS paths must be normalized. `ResetPermissions` is used by Windows encryption/attribute restore fallbacks.

Risks: `Readdirnames` must not leak open file handles on read errors. `ResetPermissions` unconditionally applies `0600`, which is a repair step rather than metadata restoration.

Test signals: `file_unix_test.go` checks FIFO directory reads do not block. `fs_local_test.go` and `node_test.go` indirectly exercise wrappers.
