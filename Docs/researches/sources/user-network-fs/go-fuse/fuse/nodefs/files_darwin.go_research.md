## sources/user-network-fs/go-fuse/fuse/nodefs/files_darwin.go

Purpose: Darwin-specific loopback file allocation and timestamp update support.

Important APIs/types/functions: `loopbackFile.Allocate` uses `F_PREALLOCATE` via `fcntl`. `timeToTimeval` converts Go time to timeval. `loopbackFile.Utimens` emulates utimens behavior using `Futimes` and helper filling for omitted times.

Control flow: lock file, invoke platform syscall, map errno/status. For nil atime/mtime, read current attrs before building timeval array.

State and persistence: mutates underlying file allocation/timestamps on disk.

Dependencies and integration: complements generic `loopbackFile` on macOS and uses `internal/utimens`.

Risks and test signals: pre-High-Sierra timestamp emulation can race with concurrent updates. Platform tests are needed for coverage.
