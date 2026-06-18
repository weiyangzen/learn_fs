# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_net.c

This file implements SMB server socket I/O wrappers and mbuf-based send/receive paths over illumos `ksocket`.

Key responsibilities:
- Creates, shuts down, and closes kernel sockets.
- Receives fixed-size buffers and mbuf chains.
- Serializes sends per SMB session through `smb_txlst_t`.
- Sends mbuf chains either by wrapping mbufs in STREAMS mblks for zero-copy or by scatter/gather UIO copying.
- Converts mbuf chains into iovec arrays using helpers from `smb_mbuf_util.c`.

Important functions:
- `smb_socreate`, `smb_soshutdown`, `smb_sodestroy`.
- `smb_sorecv` receives exactly the requested byte count using `MSG_WAITALL`.
- `smb_net_recv_mbufs` allocates an mbuf chain, builds a UIO over it, and receives into it.
- `smb_net_txl_constructor`, `smb_net_txl_destructor` initialize/destroy transmit serialization state.
- `smb_net_wrap_mbuf` wraps one mbuf as an `mblk_t` with a `frtn_t` callback.
- `smb_net_send_mblks` sends mblk chains with `ksocket_sendmblk`.
- `smb_net_send_uio` sends mbuf chains through `ksocket_sendmsg`.
- `smb_net_send_mbufs` selects mblk or UIO send path based on `smb_send_mblks`.

Concurrency and lifetime:
- `s->s_txlst.tl_active` serializes sends so only one thread writes a session socket at a time.
- Send waiters sleep on `tl_wait_cv`.
- UIO send path always frees the mbuf chain before returning.
- Mblk send path transfers mbuf ownership to STREAMS free callbacks; cleanup handles partial wrap failures.
- `smb_soshutdown` is used to interrupt blocked receive/send paths before socket close.

Performance behavior:
- Default send path is UIO scatter/gather copying.
- `smb_send_mblks` enables optional zero-copy mblk wrapping for configurations where `ksocket_sendmblk` performs better.
- Local stack iovec capacity is 16; larger sends allocate an `smb_vdb_t`-sized buffer.

Edge cases and protections:
- `smb_sorecv` returns error if `ksocket_recv` fails or returns short.
- `smb_net_recv_mbufs` frees allocated mbufs on receive/setup errors.
- `smb_net_wrap_mbuf` converts non-external mbufs to external storage when there is not enough trailing space to store `frtn_t`.
- `smb_net_send_mblks` carefully detaches/frees unwrapped remainder mbufs on wrap failure.
