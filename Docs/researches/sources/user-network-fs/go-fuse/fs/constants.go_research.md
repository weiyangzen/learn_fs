# sources/user-network-fs/go-fuse/fs/constants.go

Purpose: central constants and errno helpers for the fs package.

Important APIs: `OK` is `syscall.Errno(0)`; `ToErrno(err)` converts arbitrary errors through `fuse.ToStatus`; `RENAME_EXCHANGE` defines renameat2 exchange flag; `_SEEK_DATA` and `_SEEK_HOLE` provide lseek constants; `ENOATTR` aliases internal xattr missing-attribute errno.

Control flow/state: only `ToErrno` has logic; no mutable state.

Dependencies/integration: used broadly across bridge, loopback, memory nodes, and tests. Risks are mostly portability: numeric constants must match target OS/kernel expectations, and `ToErrno(nil)` must continue to map to success through fuse status conversion. Tests indirectly cover all constants through rename, lseek, and xattr behavior.
