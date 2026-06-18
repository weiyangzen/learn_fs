# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/sockfs/socksubr.c

## Overview
`socksubr.c` contains common sockfs support routines: initialization, vnode/device lookup, socket serialization locks, AF_UNIX address translation, ancillary data conversion, file descriptor passing, debug formatting, OOB invariant checks, sockfs kstats, file-read helpers for sendfile, and kernel/user copy helpers.

## Main Responsibilities
- Initialize sockfs global state in `sockinit()`, including vnode/vfs ops, socket cache, TPI support, direct socket support, socket parameter tables, filters, sendfile state, and the global sockfs VFS.
- Resolve transport device paths with `sogetvp()`.
- Maintain socket timestamps for stream-backed sockets via `so_update_attrs()`.
- Provide per-socket serialization helpers: `so_lock_single()`, `so_unlock_single()`, `so_lock_read()`, `so_lock_read_intr()`, and `so_unlock_read()`.
- Validate TPI offsets with `sogetoff()`.
- Translate AF_UNIX pathname addresses to internal vnode-based transport addresses.
- Convert between socket control messages and TPI options, including SCM_RIGHTS/SO_FILEP fd passing.
- Produce zone-specific AF_UNIX socket kstats.

## AF_UNIX and Address Handling
- `so_ux_lookup()` resolves a pathname, follows real vnodes through lofs, verifies `VSOCK`, checks access when requested, and finds the active sockfs vnode through the stream head.
- `so_addr_verify()` enforces family-specific sockaddr lengths for AF_INET/AF_INET6, validates AF_UNIX lengths and family, and allows opaque address forms for other families.
- `so_ux_addr_xlate()` converts an AF_UNIX pathname into a `sockaddr_ux`-style internal address based on the peer vnode pointer.

## Ancillary Data and File Descriptor Passing
- `fdbuf_create()` converts user fd integers into held `file_t *` references and audits sends.
- `fdbuf_allocmsg()` creates an external-buffer STREAMS message whose free callback closes file references.
- `fdbuf_extract()` allocates new user fds on receive, increments file reference counts, honors `MSG_CMSG_CLOEXEC` and `MSG_CMSG_CLOFORK`, and audits receives.
- `fdbuf_verify()` ensures an incoming `SO_FILEP` option matches the esballoc free-argument metadata before trusting it.
- `so_getfdopt()`, `so_optlen()`, `so_cmsg2opt()`, `so_cmsglen()`, and `so_opt2cmsg()` bridge old `msg_accrights`, modern `cmsghdr`, and internal TPI option formats.
- `so_closefds()` and `so_truncatecmsg()` clean up descriptors and adjust headers when control data is truncated or copyout fails.

## Message Allocation Helpers
- `soallocproto()`, `soallocproto1()`, `soallocproto2()`, and `soallocproto3()` allocate and populate `M_PROTO` messages with selectable sleep behavior.
- `soappendmsg()` appends zeroed or copied data into preallocated mblks.

## Debug and Invariants
- In debug builds, `pr_state()` and `pr_addr()` format socket state and addresses.
- `so_verify_oobstate()` validates legal combinations of OOB flags, mark counters, and `so_oobmsg` ownership.

## Kstats and Utility I/O
- `sock_kstat_init()` creates a per-zone raw `sock_unix_list` kstat.
- `sockfs_update()` counts active AF_UNIX sockets in the current zone.
- `sockfs_snapshot()` copies sonode state, AF_UNIX local/foreign names, vnode pointer strings, inode numbers, and zone metadata into `struct sockinfo`.
- `soreadfile()` performs cached kernel-space file reads for sendfile support.
- `so_copyin()` and `so_copyout()` switch between direct kernel copies and `xcopyin`/`xcopyout`.

## Research Notes
This file is the shared substrate that keeps sockfs syscall and STREAMS code from duplicating tricky policy. The most important correctness areas are fd-passing lifetime rules, cmsghdr/TPI length alignment, AF_UNIX vnode lifetime, and the lock ordering around sonode state and vnode/stream references.
