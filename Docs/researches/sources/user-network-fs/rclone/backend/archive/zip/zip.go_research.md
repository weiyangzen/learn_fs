# sources/user-network-fs/rclone/backend/archive/zip/zip.go

Purpose: Implements the `.zip` archiver for rclone's archive backend, exposing zip entries as a read-only rclone Fs.

Important APIs/types/functions: Registers `.zip` in `init`. `Fs` stores wrapped Fs, VFS, archive node, prefix/root, features, and `dirtree.DirTree`. `New` stats the zip file and calls `readZip`. `readZip` opens the archive node, creates `zip.NewReader`, normalizes paths, filters by root, builds directory/object tree, detects single-object roots, checks parent dirs, and sorts. Fs methods include `List`, `NewObject`, `Precision`, read-only mutators, `Hashes` returning CRC32, and unwrap/wrap. `Object` exposes size, modtime, CRC32 hash, and `Open` with seek/range support by discarding bytes or limiting the reader.

Control flow: Opening a zip eagerly scans the central directory into `dirtree`. Listing is a lookup in `dt[dir]`. `NewObject` finds an entry and rejects directories. Object open starts a fresh zip file reader, discards offset bytes for seek/range, and limits output when requested.

State and persistence: Maintains an in-memory dirtree of zip entries. Archive contents are immutable through this backend; mutators return `vfs.EROFS`. Hash state comes from zip CRC32 headers.

Dependencies and integration points: Depends on Go `archive/zip`, rclone archive registry, `dirtree`, fs/hash/log/readers/vfs, and VFS access to the underlying archive object. Instantiated by `archive.go` for `.zip` paths.

Risks: Requires known archive size; unknown-size remotes fail. Seeking is implemented by read-and-discard, which can be inefficient for large offsets. Path normalization with `path.Clean` may collapse unusual zip names. Eager central-directory reading means very large archives consume memory proportional to entry count.

Test signals: `TestArchiveZip` validates created zip archives through operations check/download, object reads, range/seek reads, modtimes, sizes, and root/subroot behavior.
