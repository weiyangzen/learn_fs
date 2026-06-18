<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/nfsd/nfssvc.c -->
# sources/user-network-fs/nfs-utils/utils/nfsd/nfssvc.c

## Purpose

`nfssvc.c` contains the low-level procfs/nfsdfs operations that let `rpc.nfsd` configure the kernel NFS server.

## Important APIs, types, and functions

Public functions include `nfssvc_mount_nfsdfs`, `nfssvc_inuse`, `nfssvc_set_sockets`, `nfssvc_set_rdmaport`, `nfssvc_set_time`, `nfssvc_get_minormask`, `nfssvc_setvers`, `nfssvc_threads`, and `nfssvc_setfh_key` as declared in the header. Private `nfssvc_setfds` creates sockets and writes their fd numbers to `/proc/fs/nfsd/portlist`; `nfssvc_print_vers` formats version tokens.

## Control flow

`nfssvc_mount_nfsdfs` checks for the `threads` file and attempts a `mount -t nfsd` if missing. `nfssvc_inuse` reads `portlist` to determine whether sockets are already configured. Socket setup resolves host/port, creates TCP/UDP IPv4/IPv6 sockets, sets IPv6-only and reuseaddr options where needed, binds/listens, then writes each fd number to `portlist` for kernel adoption. Version setup writes plus/minus version tokens to `versions`. Thread setup writes the requested count to `threads`.

## State and persistence behavior

State is kernel-owned and exposed via `/proc/fs/nfsd`. The module writes sockets, RDMA port requests, grace/lease times, lockd grace period, supported versions, and thread counts. A static scratch `buf[128]` is reused across operations.

## Dependencies and integration points

It depends on Linux nfsdfs paths, socket APIs, `getaddrinfo`, support NFS macros, `version.h`, and `xlog`. `nfsd.c` is its primary caller.

## Risks and edge cases

`nfssvc_get_minormask` reads into a 128-byte buffer and then writes `ptr[size] = '\0'`; if `read` returns the full buffer length, this is an out-of-bounds write. Socket setup returns success if at least one socket was handed off, even if later addresses fail. The fallback `system("/bin/mount ...")` ignores direct return status. Version formatting depends on kernel version for v4.0 syntax.

## Test signals

Tests should cover nfsdfs absent/present, portlist read states, IPv4/IPv6 socket handoff, partial address failures, service-name fallback from `nfs` to `2049`, RDMA port names and numbers, version-string formatting around Linux 4.11, minor mask parsing at buffer boundaries, grace/lease writes, and thread-file fallback.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/nfsd/nfssvc.c -->
