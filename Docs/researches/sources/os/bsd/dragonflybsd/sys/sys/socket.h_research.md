# File Research: sources/os/bsd/dragonflybsd/sys/sys/socket.h

This header defines the primary socket user ABI: socket types, options, address families, socket address structures, message and control-message formats, shutdown constants, sendfile header/trailer structure, and socket syscall declarations.

Key responsibilities:
- Defines socket-related types:
  - `sa_family_t`
  - `socklen_t`
  - BSD-visible `gid_t`, `uid_t`, and `off_t`
- Defines socket types and BSD socket creation flags:
  - `SOCK_STREAM`, `SOCK_DGRAM`, `SOCK_RAW`, `SOCK_SEQPACKET`, BSD `SOCK_RDM`
  - `SOCK_CLOEXEC`, `SOCK_NONBLOCK`, `SOCK_CLOFORK`
  - kernel `SOCK_KERN_NOINHERIT`
- Defines socket options:
  - `SO_DEBUG`, `SO_ACCEPTCONN`, `SO_REUSEADDR`, `SO_KEEPALIVE`, `SO_LINGER`, etc.
  - buffer/time/error/type options `SO_SNDBUF`, `SO_RCVBUF`, `SO_ERROR`, `SO_TYPE`
  - DragonFly/BSD additions such as `SO_USER_COOKIE` and `SO_CPUHINT`
- Defines `struct linger` and BSD `struct accept_filter_arg`.
- Defines `SOL_SOCKET`.
- Defines address families and BSD-visible protocol family aliases.
- Defines `struct sockaddr`, `SOCK_MAXADDRLEN`, kernel `sa_equal()`, `struct sockproto`, and `struct sockaddr_storage`.
- Defines network sysctl constants such as `NET_RT_DUMP`, `NET_RT_FLAGS`, and `NET_RT_IFLIST`.
- Defines listen and sockopt limits:
  - `SOMAXCONN`
  - `SOMAXOPT_SIZE`
  - `SOMAXOPT_SIZE0`
- Defines `struct msghdr`, message flags, `struct cmsghdr`, credential ancillary data, and `CMSG_*` macros.
- Defines control message types:
  - `SCM_RIGHTS`
  - BSD `SCM_TIMESTAMP`
  - BSD `SCM_CREDS`
- Defines shutdown constants `SHUT_RD`, `SHUT_WR`, `SHUT_RDWR`.
- Defines BSD `struct sf_hdtr` for `sendfile()`.
- Declares socket syscalls and BSD extensions:
  - standard socket, bind, connect, listen, accept, send, recv, getsockopt, setsockopt, shutdown
  - `accept4`, `extaccept`, `extconnect`, `pfctlinput`, `sendfile`

Important invariants:
- `struct sockaddr` uses a length byte and family byte, BSD style.
- `struct sockaddr_storage` is 128 bytes and aligned using an `__int64_t` field.
- `CMSG_NXTHDR()` performs bounds checking against `msg_controllen`.
- `MSG_FBLOCKING` and `MSG_FNONBLOCKING` override `FIONBIO`; their mask is `MSG_FMASK`.
- `SOMAXOPT_SIZE0` allows larger root `getsockopt()` payloads.

Research notes:
- This is one of the core network ABI headers and must remain stable for userland compatibility.
