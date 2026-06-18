## sources/user-network-fs/go-fuse/fuse/direntry_linux.go

Purpose: Linux-specific raw `getdents` entry layout support.

Important APIs/types/functions: `dirent` mirrors Linux dirent fields and `nameLength` computes name bytes from record length.

Control flow: generic directory parsing reads this structure from byte buffers.

State and persistence: stateless.

Dependencies and integration: used by `NewLoopbackDirStream` and directory tests on Linux.

Risks and test signals: bad name length or alignment produces corrupted directory names or skipped entries; readdir stress tests expose this quickly.
