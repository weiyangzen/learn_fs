# File Research: sources/local-fs/xfsdump/librmt/isrmt.c

Implements `isrmt(fd)`.

Behavior:
- Returns true when `fd >= REM_BIAS`.
- Remote descriptors are represented by adding `REM_BIAS` to an internal remote-unit index.

Role:
- Lets wrapper functions choose local syscall path versus remote protocol path.
