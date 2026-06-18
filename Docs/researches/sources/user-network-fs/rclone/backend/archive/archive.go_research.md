# sources/user-network-fs/rclone/backend/archive/archive.go

Purpose: Implements rclone's `archive` wrapper backend for reading archive files inside another remote as virtual directories, with `.zip` and `.sqfs` archivers registered by side-effect imports.

Important APIs/types/functions: Registers backend `archive` with optional `remote`. `Options` has `Remote`. `Fs` wraps an upstream `fs.Fs`, tracks root/features/wrapper, and caches discovered `archive` instances in `archives`. Helpers `findArchive`, `subArchive`, `(*archive).init`, `NewFs`, `findFs`, `List`, and `NewObject` define archive discovery and lazy opening. It implements many optional interfaces by delegating to the wrapped Fs: `Purge`, `Copy`, `Move`, `DirMove`, `ChangeNotify`, `DirCacheFlush`, `Put`, `PutStream`, `About`, `Shutdown`, `PublicLink`, `PutUnchecked`, `MergeDirs`, `CleanUp`, `OpenWriterAt`, `OpenChunkWriter`, `UserInfo`, and `Disconnect`.

Control flow: `NewFs` parses the configured remote/root, detects if the requested path is inside an archive by walking parent paths, opens the underlying remote via `cache.Get`, creates wrapper features by masking with the upstream, and either returns an initialized archive Fs when the root itself is an archive or returns the wrapper Fs. `List` delegates to the relevant sub-Fs and replaces recognized archive objects with directory entries. `NewObject` routes object lookup to the wrapped Fs or an initialized archive Fs based on the containing directory.

State and persistence: Maintains `archives` map of discovered archive paths and each archive's lazily initialized Fs under mutexes. Underlying remote state is external. Archive contents are read-only from concrete archiver implementations.

Dependencies and integration points: Depends on rclone `fs`, `cache`, `fspath`, config parsing, hash interfaces, archive `archiver` registry, and side-effect imports for squashfs/zip. Integrates with VFS through concrete archivers.

Risks: Archive lookup uses linear searches and an unordered map; comments note nested archive longest-prefix handling may be wrong. Archive writes are mostly delegated to underlying remote, which can make wrapper semantics subtle. Plan9 is unsupported by build tags.

Test signals: `archive_internal_test.go` creates zip/squashfs archives and checks list/read/range/seek behavior. `archive_test.go` runs fstests over local/memory archive configurations.
