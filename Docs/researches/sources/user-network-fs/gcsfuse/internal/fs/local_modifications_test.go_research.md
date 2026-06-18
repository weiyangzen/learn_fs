# sources/user-network-fs/gcsfuse/internal/fs/local_modifications_test.go

Purpose: broad integration contract for modifying a GCS-backed FUSE filesystem through normal local filesystem APIs. It covers open flags, legal filenames, mknod, modes, directories, file data operations, sync/close persistence, symlinks, and rename behavior.

Important APIs/types: suites are ogletest-style (`OpenTest`, `MknodTest`, `ModesTest`, `DirectoryTest`, `FileTest`, `SymlinkTest`, `RenameTest`) embedding `fsTest`. Helpers include `interestingLegalNames`, which generates Unicode, shell-special, control/space-category, and max-length names, `getFileOffset`, `validateObjectAttributes`, and `createFile`.

Control flow and state: open tests validate nonexistent opens, create-on-open, truncation, multiple handles observing each other, legal and illegal names. Mode tests validate read-only/write-only/read-write errors and writes, append behavior, `WriteAt` offset preservation, and sparse writes with zero filling. Directory tests cover `Mkdir`, stat/read entries, non-empty and open rmdir, recreation with same name, unsupported hard links, chmod/chtimes no-op success, timestamp reasonableness, and GCS content type for directory marker objects.

Persistence behavior: file tests verify writes past EOF, truncation, seek, stat/lstat, unlink while open, bucket-side deletion races, same-name recreation, chmod/chtimes, dirty and clean sync, clobbered sync/close preserving the newer bucket generation, and content-type retention. Attribute tests compare extended GCS object attributes before and after append/write-at to ensure rewrites preserve relevant metadata while creating a new generation.

Symlink and rename integration: symlink creation writes legacy `gcsfuse_symlink_target` metadata and supports readlink/lstat/stat/remove. Rename tests cover directory naming conflicts, recursive directory rename limits, nested directories, cross-directory file moves, cross-device failures, overwrite semantics, wrong-type errors, and missing sources.

Dependencies: uses `os`, `syscall`, `storageutil`, fake GCS bucket, `gcs`, integration operations helpers, fusetesting, ogletest, and runtime-specific name limits.

Risks: large suite is environment-sensitive, especially kernel/FUSE error text, name limits, writeback caching, and time slop. It encodes both legacy symlink metadata and generation-clobber safety, making it a high-signal migration guard.
