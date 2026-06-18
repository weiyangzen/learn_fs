## sources/user-network-fs/go-fuse/fuse/nodefs/syscall_linux.go

Purpose: Linux syscall wrapper used by nodefs file timestamp updates.

Important APIs/types/functions: `futimens` wraps the appropriate Linux syscall for setting file descriptor timestamps from `Timespec` values.

Control flow: called by `loopbackFile.Utimens` after building atime/mtime timespecs.

State and persistence: mutates timestamps of the file referenced by fd.

Dependencies and integration: Linux companion to `files_linux.go`.

Risks and test signals: syscall number/signature mistakes break `utimens` through nodefs loopback files.
