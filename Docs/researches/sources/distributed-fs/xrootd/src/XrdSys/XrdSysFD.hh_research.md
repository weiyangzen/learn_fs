## sources/distributed-fs/xrootd/src/XrdSys/XrdSysFD.hh

Purpose: provides inline wrappers for common file descriptor creation APIs that set `FD_CLOEXEC` portably.

Important APIs/types/functions: anonymous-namespace wrappers `XrdSysFD_Accept`, `XrdSysFD_Dup`, `XrdSysFD_Dup1`, `XrdSysFD_Dup2`, `XrdSysFD_Open`, `XrdSysFD_OpenDir`, `XrdSysFD_Pipe`, `XrdSysFD_Socket`, `XrdSysFD_Socketpair`, `XrdSysFD_Openat`, and `XrdSysFD_Yield`.

Control flow: on Linux/GNU with `SOCK_CLOEXEC` and `O_CLOEXEC`, wrappers use atomic CLOEXEC variants such as `accept4`, `dup3`, `pipe2`, and `socket(...|SOCK_CLOEXEC)`. Fallbacks call traditional APIs then `fcntl(F_SETFD, FD_CLOEXEC)`.

State and persistence: no owned state. Wrappers return descriptors/directories whose lifecycle belongs to callers. `XrdSysFD_Yield()` clears `FD_CLOEXEC` on an existing descriptor.

Dependencies and integration: POSIX file, socket, directory, and errno headers. Used by logger, poller, plugin-adjacent code, and other subprocess-safe components.

Risks: fallback paths have an unavoidable fork/exec race between descriptor creation and `fcntl`. `Dup2` fallback returns `dup2` status, whose zero success assumption only holds when duplicating to descriptor 0; this deserves careful review. `openat` always ORs `O_CLOEXEC`, assuming it exists.

Test signals: descriptor flags after every wrapper, fallback builds, `OpenDir` error preservation, `Yield()` clearing, and fork/exec leak checks.
