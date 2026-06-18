# sources/user-network-fs/go-fuse/fs/files.go

Purpose: implements `LoopbackFile`, a file-handle wrapper around a Unix fd that satisfies most file-level go-fuse interfaces.

Important APIs/functions: `NewLoopbackFile`; `PassthroughFd`; `Read` returns `fuse.ReadResultFd`; `Write` uses `Pwrite`; `Release` closes once; `Flush` closes a dup; `Fsync`; OFD/flock locking through `Getlk`, `Setlk`, `Setlkw`; `Setattr`/`setAttr` handle chmod/chown/times/truncate; `Getattr`; `Lseek`; `Allocate`; ioctl passthrough; platform-specific `utimens`.

Control flow/state: fd protected by `mu`; `Release` marks fd `-1`. Operations serialize on the file handle.

Dependencies/integration: used by `LoopbackNode.Open/Create`; integrates fallocate, ioctl, unix syscalls, passthrough backing FDs. Risks include operations after release, serializing all I/O on one mutex, syscall portability, and fd ownership requirements documented by `NewLoopbackFile`. Tests cover loopback reads/writes, ioctl, copy, stat, direct I/O, and mount behavior.
