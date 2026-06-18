## sources/user-network-fs/libtirpc/src/epoll_sub.c

Purpose: Supplies direct syscall wrappers for `epoll_create`, `epoll_ctl`, and `epoll_wait` on systems/builds where libc lacks these entry points.

Important APIs and control flow: Defines syscall numbers `254`, `255`, and `256`, then each public function simply calls `syscall` with the corresponding number and arguments.

State and persistence: No local state. Kernel epoll instances and interest lists are managed by the returned file descriptors and syscalls.

Dependencies and integration: Depends on Linux syscall numbering for a specific architecture family and `<sys/epoll.h>` structures. It is a portability shim rather than RPC logic.

Risks and test signals: Hard-coded syscall numbers are architecture-sensitive. Tests should compile only on intended targets, compare wrapper behavior to libc epoll when available, verify errno propagation, and guard builds for unsupported architectures.
