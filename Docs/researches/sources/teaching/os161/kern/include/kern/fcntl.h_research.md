# File Research: sources/teaching/os161/kern/include/kern/fcntl.h

Defines open flags, file-control constants, and `struct flock`.

Key contents:
- Access modes: `O_RDONLY`, `O_WRONLY`, `O_RDWR`, mask `O_ACCMODE`.
- Open modifiers: `O_CREAT`, `O_EXCL`, `O_TRUNC`, `O_APPEND`, `O_NOCTTY`.
- Lock and fcntl operation constants.
- `struct flock` with start, whence, type, length, and pid.

Relevance:
- SFS and semfs directory open handlers reject write/RDWR/append on directories.
- semfs create behavior uses exclusive-create semantics passed by VFS.
