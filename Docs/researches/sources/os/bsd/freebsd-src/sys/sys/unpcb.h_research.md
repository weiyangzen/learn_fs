# File Research: sources/os/bsd/freebsd-src/sys/sys/unpcb.h

UNIX-domain socket protocol control block and exported sysctl record header.

Key responsibilities:
- Defines generation counter type `unp_gen_t`.
- Under kernel or `_WANT_UNPCB`, defines `struct unpcb` with PCB lock, connection pointer, atomic refcount, flags, garbage-collector flags, bound address, socket pointer, pair-lock busy count, vnode association, peer credentials, reference-list linkage, all-PCB linkage, refs head, generation count, file back-pointer, message/reference counts, fake inode/mode, and dead-list linkage.
- Defines PCB flags for peer credential availability, credential passing, connecting/binding/waiting state, and garbage-collector state.
- Provides `sotounpcb()` cast macro.
- When socketvar is included, defines exported `struct xunpcb` and `struct xunpgen` sysctl records with stable kernel-address-sized fields and sockaddr copies.
- Declares kernel peer-credential copy helper.

Dependencies:
- Uses queue and ucred headers, socket/vnode/file types, cache-line alignment, socketvar export types, and UNIX socket address definitions.

Notable risks:
- The locking key distinguishes atomic, constant, PCB lock, linkage lock, and list lock fields; misusing these can race connection teardown or garbage collection.
- Exported sysctl structures include kernel addresses for observability and ABI compatibility, so field changes affect tools like netstat and fstat.
