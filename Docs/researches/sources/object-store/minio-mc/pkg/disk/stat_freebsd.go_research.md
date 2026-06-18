## sources/object-store/minio-mc/pkg/disk/stat_freebsd.go

Purpose: FreeBSD implementation of `GetFileSystemAttrs`, emitting mode, owner, group, access time, and modification time as a slash-separated metadata string.

Control flow performs `syscall.Stat`, formats `Atimespec` and `Mtimespec` seconds/nanoseconds with explicit `int64` casts, appends numeric IDs, and conditionally appends resolved user/group names. State is read-only filesystem metadata. Dependencies are `syscall`, `os/user`, `strconv`, and `strings`. Integration is cross-platform attribute preservation. Risks include silent omission of names, separator collisions in names, and platform-specific build coverage. The comment references an issue requiring int64 casts, making regression tests or build checks on FreeBSD valuable.
