# sources/object-store/minio/cmd/is-dir-empty_linux.go

## Purpose

`is-dir-empty_linux.go` provides the Linux implementation of `isDirEmpty`, optimized for filesystems where a directory with no children has link count 2.

## Important APIs, Types, And Control Flow

The build tag selects Linux except App Engine. `isDirEmpty(dirname, legacy)` has two paths. In legacy mode it calls `readDirN(dirname, 1)` and returns true only when the read succeeds and yields no entries. In the optimized mode it calls `syscall.Stat`, confirms the path is a directory via `S_IFMT == S_IFDIR`, and returns true when `Nlink == 2`.

## State, Dependencies, Integration, Risks, And Tests

There is no persistent state. Dependencies are `syscall.Stat` and package-local `readDirN`. The function is intended for metadata/object-store filesystem scanning where checking emptiness cheaply matters. The main risk is filesystem-specific link-count behavior: the comment explicitly calls out btrfs and NFS as cases where the optimization is unreliable, hence the legacy fallback. Other risks are races between stat/read and concurrent creates/deletes, symlink/stat semantics, and platform differences hidden behind build tags. No direct tests are present in this subset.
