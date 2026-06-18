# File Research: sources/os/bsd/freebsd-src/sys/sys/socket.h

Primary public socket ABI header.

Key responsibilities:
- Defines socket types, creation flags, socket options, timestamp modes, and option levels.
- Defines address families, protocol family aliases, routing sysctl constants, and vendor-reserved AF ranges.
- Defines `sockaddr`, `sockproto`, `sockaddr_storage`, `msghdr`, `cmsghdr`, credential control-message structures, and ancillary data macros.
- Defines message flags for send/receive operations, including BSD, POSIX, and kernel-only extensions.
- Defines control-message types such as `SCM_RIGHTS`, timestamps, credentials, and timestamp info.
- Defines shutdown modes, `sendfile(2)` header/trailer structures and flags, `mmsghdr`, and splice option structure.
- Declares userspace socket syscalls and FreeBSD extensions such as `accept4()`, `bindat()`, `connectat()`, `sendfile()`, `sendmmsg()`, and `recvmmsg()`.

Important patterns:
- Visibility macros separate POSIX, BSD, and kernel-only constants.
- Ancillary data layout uses `_ALIGN()` for portable control-message traversal.
- Socket options are split between bit flags stored in `so_options` and numbered get/set options.
- `MSG_NBIO` is explicitly noted as used by fifofs, linking socket flags to filesystem FIFO behavior.

Research relevance:
- Canonical userspace/kernel ABI for socket I/O, ancillary data, sendfile, and local descriptor passing.
