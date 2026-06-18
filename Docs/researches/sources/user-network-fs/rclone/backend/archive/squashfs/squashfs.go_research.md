# sources/user-network-fs/rclone/backend/archive/squashfs/squashfs.go

Purpose: Implements the `.sqfs` archiver for rclone's archive backend, exposing squashfs contents as a read-only rclone Fs.

Important APIs/types/functions: Registers `.sqfs` in `init`. `Fs` stores wrapped Fs, VFS, squashfs filesystem handle, cache, archive node, prefix/root, and features. `New` creates VFS with zero read wait, stats the archive, builds cache, calls `squashfs.Read`, adjusts root when pointing to a single file, and sets features. Path helpers `toNative`, `fromNative`, `objectFromFileInfo`, `newObjectNative`. Fs methods `List`, `NewObject`, `Precision`, read-only mutators, `Hashes`, unwrap/wrap. `Object` stores size, modtime, and `squashfs.FileStat`; `Open` supports `SeekOption` and `RangeOption`.

Control flow: Listings translate rclone remotes into native squashfs paths, read directory entries from go-diskfs, create dirs or regular file objects, and skip non-regular files. Object lookup reads parent directory and finds a matching leaf. Opening an object calls the squashfs file stat's `Open`, seeks if needed, and wraps limited reads for ranges.

State and persistence: Keeps parsed squashfs handle and VFS/cache state in memory. Archive contents are read-only; mutations return `vfs.EROFS`. Hashes are unsupported.

Dependencies and integration points: Depends on go-diskfs squashfs, archive registry, rclone fs/hash/log/readers/vfs/vfscommon. Instantiated through `archive.go` when `.sqfs` is discovered.

Risks: Non-regular entries are skipped. Some comments indicate unfinished single-object handling and blocksize tuning. Path translation must correctly handle prefix/root or objects can disappear. Cache close lifecycle is not visibly tied to Fs shutdown in this file.

Test signals: `TestArchiveSquashfs` validates generated squashfs archives, subdirectory/single-file roots, range/seek reads, modtimes, sizes, and full-tree checks.
