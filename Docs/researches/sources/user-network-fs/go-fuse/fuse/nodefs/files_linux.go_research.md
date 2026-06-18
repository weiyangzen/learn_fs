## sources/user-network-fs/go-fuse/fuse/nodefs/files_linux.go

Purpose: Linux-specific loopback file allocation and timestamp updates.

Important APIs/types/functions: `loopbackFile.Allocate` wraps `syscall.Fallocate`. `loopbackFile.Utimens` builds two `Timespec`s using `fuse.UtimeToTimespec` and calls `futimens`.

Control flow: lock file fd, call syscall, convert errors to `fuse.Status`.

State and persistence: mutates underlying file allocation and timestamps on disk.

Dependencies and integration: used by nodefs loopback files and POSIX truncate/fallocate/timestamp tests.

Risks and test signals: keep-size/allocation mode support depends on kernel and filesystem. Errors propagate to FUSE callers through `ToStatus`.
