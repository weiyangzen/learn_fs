# sources/sync-backup/syncthing/lib/model/folder_test.go

Purpose: this test file covers folder-level utility behavior, primarily scan subdirectory normalization through `unifySubs` and platform-data application through `sendReceiveFolder.setPlatformData`.

Important types and helpers: `unifySubsCase` describes input subdirectories, paths known to exist in the database, and expected normalized output. `unifySubsCases` returns platform-adjusted cases, converting slash separators on Windows. The tests use `messagediff` for readable output differences and `slices.Contains` to implement a fake existence predicate.

Control flow covered by `TestUnifySubs`: trailing slash cleanup, deterministic sorting, subsumption of child paths by parent paths, interpreting `nil`, empty input, or explicit empty string as full-folder scan, preserving unknown children when a known parent exists, distinguishing true path prefixes from lexical prefixes such as `usr/lib` vs `usr/libexec`, preserving special files `.stfolder` and `.stignore`, falling back to scanning a known parent when an unknown path cannot be trusted, and cleaning absolute paths into folder-relative paths.

`BenchmarkUnifySubs` repeatedly runs the same cases to track allocation and performance behavior. This matters because subdirectory scan requests can be a frequent control path when file watchers or users request partial rescans.

`TestSetPlatformData` creates a fake filesystem, writes a temp file, constructs a `protocol.FileInfo` whose `Name` intentionally does not match the target path, sets permissions, modified time, and xattrs for Linux, Darwin, FreeBSD, and NetBSD, and calls `setPlatformData` with `SyncXattrs` enabled. The intent is to ensure platform metadata is applied to the explicit path argument and does not accidentally depend on `FileInfo.Name`.

State and persistence behavior: `TestUnifySubs` is pure, using only a fake database-existence callback. `TestSetPlatformData` mutates a fake filesystem and validates no error from xattr/permission/time application. No model database is used directly.

Dependencies and integration points: tests exercise `config.DefaultMarkerName`, `config.XattrFilter`, `fs.NewFilesystem`, `protocol.PlatformData`, scanner-compatible file metadata, build platform detection, and `sendReceiveFolder`'s embedded `folder` configuration. The xattr test is a cross-platform compatibility signal for the platform-specific send/receive files.

Risks: `unifySubs` must avoid overscanning too broadly while never missing necessary paths; special marker and ignore files are exceptions to normal existence logic. Platform-data application must not trust remote file names for local path selection. Coverage is strong for representative normalization cases but not exhaustive for all path-cleaning edge cases or every platform xattr implementation.
