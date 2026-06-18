# File Research: sources/os/bsd/netbsd-src/sys/sys/kauth.h

Defines NetBSD’s kernel authorization framework: scopes, listeners, action IDs, vnode action bitmasks, credential APIs, and authorization wrappers. It covers generic, system, process, network, machdep, device, credential, and vnode policy spaces. Under `__KAUTH_PRIVATE`, it exposes the credential layout used by debugger/kvm consumers.

Filesystem relevance is substantial: vnode actions encode read/write/execute/delete/attribute/extattr/security/flag/link operations, and system requests include mount, quota, LFS, extattr, snapshots, reserved space, and interrupt affinity. Risks are policy bypass from wrong action/subaction pairing, vnode remote-filesystem semantics via `KAUTH_VNODE_REMOTEFS`, credential reference lifetime, and ABI synchronization of private credential layout with kvm consumers.
