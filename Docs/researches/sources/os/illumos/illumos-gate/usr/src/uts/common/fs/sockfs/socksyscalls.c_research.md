# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/sockfs/socksyscalls.c

## Overview
`socksyscalls.c` implements the kernel side of socket-related system calls and sendfile support. It maps user file descriptors to sonodes, copies user arguments safely, delegates protocol behavior to the socket operation layer, handles legacy ABI differences, manages socket configuration/filter registration, and implements sendfile through direct I/O or page-cache-backed transmission.

## Main Responsibilities
- Implement `socket`, `socketpair`, `bind`, `listen`, `accept`, `connect`, `shutdown`, `recv`, `recvfrom`, `recvmsg`, `send`, `sendmsg`, `sendto`, `getpeername`, `getsockname`, `getsockopt`, and `setsockopt`.
- Provide `getsonode()` fd-to-sonode lookup with namefs/stream-head awareness.
- Copy in and normalize sockaddr arguments with `copyin_name()`, including AF_UNIX NUL termination.
- Copy out addresses/options with XNET-compatible truncation semantics.
- Register/remove socket transports and filters through `sockconfig()`.
- Implement `sendfile` backing paths: asynchronous direct I/O, zero-copy segmap/vpm, and cached read/send loops.
- Provide 32-bit syscall wrappers and legacy compatibility wrappers around the sonode operation switch.

## Syscall Path Details
- `so_socket()` validates type flags, optionally copies a transport device path, creates the socket, allocates a file descriptor, sets nonblocking/ndelay state, and applies close-on-exec/close-on-fork flags.
- `so_socketpair()` builds AF_UNIX datagram pairs by binding and cross-connecting both endpoints; stream pairs are made with a listener, nonblocking connect, accept, and fd replacement.
- `accept()` preallocates a user fd before consuming a connection, optionally copies out peer address, creates a file structure, applies accept flags, and propagates listener nonblocking state.
- `recvit()` and `sendit()` are the common receive/send workers. They set `uio` flags from the file, handle address/control copyin or copyout, and delegate to `socket_recvmsg()`/`socket_sendmsg()`.
- `recvmsg()` and `sendmsg()` translate native and ILP32 structures, bound iovec counts, reject negative or overflowing lengths, and preserve legacy non-XPG behavior.

## Compatibility Semantics
- Non-XPG send paths force `MSG_EOR` to match older libsocket/sockmod behavior.
- Old `msg_accrights` style control data is supported separately from modern `cmsghdr` control data.
- 32-bit callers get iovec widening and timeval/timespec-compatible ancillary handling through the shared subroutines.
- `copyout_name()` reports the full kernel length even when the user buffer truncates, matching XNET semantics.

## Sockconfig and Filters
- `sockconf_add_sock()` installs socket parameter mappings either for `/dev/...` transports or named socket modules.
- `sockconfig_add_filter()` copies filter properties, validates hints and socket tuples, supports ILP32 property translation, and adds auto or programmatic socket filters.
- Removal marks filters condemned if still referenced, otherwise frees them immediately.
- `sockconfig()` requires network configuration privilege and dispatches add/remove/get-table commands.

## Sendfile Implementation
- `sendfile_init()` initializes the sendfile request queue, service-thread limits, timeout, and default cache policy.
- Direct I/O uses `create_thread()` and `snf_async_thread()` to run `snf_async_read()` as a producer, queueing mblks with high/low water flow control. `snf_direct_io()` consumes queued mblks and sends them with `socket_sendmblk()`.
- `snf_segmap()` uses vpm mappings when available, otherwise segmap soft locks, builds zero-copy esballoc mblks, marks `STRUIO_ZC`, and optionally waits for zero-copy completion unless `SFV_NOWAIT` is set.
- `snf_cache()` reads file data into allocated mblks and sends them, adjusting chunk sizes for stream/socket max packet sizes and active socket filters.
- `sosendfile64()` chooses direct I/O when the transfer exceeds `sendfile_max_size`; otherwise it validates file size, decides if zero-copy is worthwhile and safe, and falls back to cached copying.

## Error Handling and Lifetime
- All syscall entry points release held file descriptors on each exit path.
- Copyin/copyout failures return `EFAULT`; excessive user-controlled sizes return `EINVAL` or `EMSGSIZE`.
- Sendfile direct I/O coordinates read/write errors so write errors win when both sides fail, drains queued mblks on failure, and always waits for the reader to finish.
- Zero-copy sendfile callbacks release vpm/segmap mappings and held vnodes only after the mblk data block’s last reference is dropped.

## Research Notes
This file is the user/kernel ABI surface for sockfs. Its highest-risk areas are argument translation across ABI versions, fd lifetime during socketpair/accept/sendmsg/recvmsg, privilege-checked dynamic configuration, and sendfile’s interaction with vnode locking, zero-copy completion, active socket filters, and partial-transfer accounting.
