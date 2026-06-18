# File Research: sources/os/bsd/netbsd-src/sys/fs/nfs/common/nfs_mountcommon.h

This header defines common fields shared by NFS client mount structures for lock-manager integration.

Key contents:
- Declares callback typedefs for extracting vnode/NFS info and invalidating buffers.
- Defines `struct nfsmount_common` with mutex, mount flags/state, mount pointer, timeout/retry values, hostname, and two client-specific callback pointers.
- Intended to let the NLM code interact with multiple NFS client implementations through a common subset.

Important dependencies:
- Used by lock code and client mount structures.
- Depends on vnode, sockaddr, mount, lwp, and timeval types.

Risks and notes:
- The callback fields are the main abstraction boundary; lockd correctness depends on clients returning compatible file handle/address/version data.
