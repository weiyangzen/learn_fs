# sources/object-store/minio-mc/cmd/client-fs.go

## Purpose

`client-fs.go` implements the local filesystem backend for the shared `Client` interface. It lets mc commands treat POSIX/Windows paths like object-storage URLs for copy, list, stat, remove, bucket-like directory creation, watch, and metadata-preservation flows. The file deliberately returns `APINotImplemented` for S3-only features such as select, bucket policies beyond chmod-style access, object lock, tags, lifecycle, versioning, replication, encryption, restore, multipart object-download parts, and CORS.

## Important APIs, Types, And Control Flow

The central type is `fsClient`, which stores a normalized `ClientURL`. `fsNew` validates and absolutizes paths, preserving a trailing separator because listing uses it to distinguish "list this directory" from "treat this path as a prefix". `Put` delegates to `put`; `PutPart` uses `putN` when a nonnegative byte count is supplied. Both write through a UUID-named temp file in the target directory, copy data with `hookreader.NewHook` for progress, close the descriptor before rename for Windows compatibility, validate expected size, and atomically commit with `os.Rename`. Attribute preservation parses mc metadata, applies chmod/chown while writing, then restores atime/mtime after rename.

`Get`, `Stat`, and `List` translate file metadata into `ClientContent`. `List` chooses recursive walking, directory-first/last recursion, or nonrecursive prefix behavior, then filters `.part.minio` incomplete artifacts. `Remove` consumes `ClientContent` values and deletes files, incomplete parts, and empty parent directories within the original base path. `Watch` maps mc event names onto platform notify events and emits S3-style `EventInfo`.

## State, Dependencies, Integration, Risks, And Tests

Persistent state is the host filesystem: created directories, renamed temp files, chmod/chown timestamps, xattrs, and `.part.minio` suffixes. Dependencies include `os`, `filepath`, `syscall`, `rjeczalik/notify`, `pkg/xattr`, `disk.GetFileSystemAttrs`, and shared mc errors. Important risks are path-length differences, recursive deletion escaping the base path, symlink stat behavior, platform event differences, unsupported xattr handling, and chmod/chown failures during preserve mode. `client-fs_test.go` covers put/get/stat/copy/list/mkdir/access basics, range-style reading, recursive listing, and OS-specific ignore behavior.
