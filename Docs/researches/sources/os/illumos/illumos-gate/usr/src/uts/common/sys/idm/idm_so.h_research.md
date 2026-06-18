# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/idm/idm_so.h

This header declares the sockets transport implementation pieces for IDM.

Key definitions:
- Socket buffer sizes: `IDM_RCVBUF_SIZE`, `IDM_SNDBUF_SIZE` at 256 KiB.
- Socket buffer cache range: `IDM_SO_BUF_CACHE_LB` 32 KiB and `IDM_SO_BUF_CACHE_UB` 128 KiB.
- `idm_so_svc_t` stores service socket, service thread, thread ID, and running flag.
- `idm_so_conn_t` stores connection socket, TX/RX threads, thread IDs, running flags, TX mutex/CV, and TX PDU list.
- `idm_so_timed_socket_t` stores CV/callback/error state for timed socket connect.

Functions:
- Transport init/fini: `idm_so_init`, `idm_so_fini`.
- Socket lifecycle: `idm_socreate`, `idm_soshutdown`, `idm_sodestroy`.
- Address utilities: sockaddr comparison, IP address list retrieval, IDM address to sockaddr, sockaddr to presentation string.
- I/O helpers: `idm_sorecv`, `idm_sosendto`, `idm_iov_sosend`, `idm_iov_sorecv`.
- TX/RX threads and PDU cache constructors/destructors.
- Service port watcher and timed socket connect.

Dependencies:
- Includes `sys/idm/idm_transport.h` and `sys/ksocket.h`.

Relevance:
- Implements TCP socket data movement for iSCSI when not using iSER/RDMA. Directly relevant to block storage networking.
