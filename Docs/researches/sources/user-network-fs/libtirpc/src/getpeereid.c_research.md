## sources/user-network-fs/libtirpc/src/getpeereid.c

Purpose: Provides a fallback `getpeereid` implementation when the platform does not supply one.

Important APIs and control flow: Under `!HAVE_GETPEEREID`, `getpeereid(int s, uid_t *euid, gid_t *egid)` calls `getsockopt(SOL_SOCKET, SO_PEERCRED)` into `struct ucred`, then copies `uc.uid` and `uc.gid` to outputs.

State and persistence: No persistent state. It reads peer credential state maintained by the kernel for a connected Unix-domain socket.

Dependencies and integration: Used by local transport authentication paths needing peer uid/gid. Linux-specific `SO_PEERCRED` semantics are assumed.

Risks and test signals: Output pointers are not checked for null. Tests should use socketpairs with known credentials, verify error propagation on invalid sockets, and confirm compile guards exclude this implementation where libc provides `getpeereid`.
