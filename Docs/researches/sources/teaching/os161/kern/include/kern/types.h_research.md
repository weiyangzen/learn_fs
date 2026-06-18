# File Research: sources/teaching/os161/kern/include/kern/types.h

Defines machine-independent private ABI typedefs.

Key types:
- Filesystem/storage: `__blkcnt_t`, `__blksize_t`, `__daddr_t`, `__dev_t`, `__fsid_t`, `__ino_t`, `__mode_t`, `__nlink_t`, `__off_t`.
- Process/credentials/time/resource/socket: pid, uid/gid, rlim, time, sockaddr family, socklen, nfds.
- Includes machine-dependent primitive integer types first.

Relevance:
- All public kernel/user ABI headers build standard type names from these private typedefs.
- SFS block numbers, stat fields, offsets, and device attributes depend on these definitions.
