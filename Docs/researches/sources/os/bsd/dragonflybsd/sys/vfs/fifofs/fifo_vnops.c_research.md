# File Research: sources/os/bsd/dragonflybsd/sys/vfs/fifofs/fifo_vnops.c

Implements generic FIFO vnode operations using a connected pair of local stream sockets. It registers `fifo_vnode_vops` via `VNODEOP_SET`.

`struct fifoinfo` stores read socket, write socket, reader count, and writer count. A pool of 128 hashed locks serializes open/close transitions for FIFO vnodes that may otherwise use shared vnode locks.

`fifo_fip_create` allocates FIFO state, creates two `AF_LOCAL` stream sockets, connects them with `unp_connect2`, disables linger, sets write low water to `PIPE_BUF`, and initially marks the read side unable to receive until readers/writers connect. `fifo_fip_destroy` closes both sockets and frees state.

`fifo_open` creates `v_fifoinfo` on first open, adjusts reader/writer counters, reconnects/disconnects sockets as needed, implements blocking open semantics for readers/writers, returns `ENXIO` for nonblocking write opens with no readers, sets `VNOTSEEKABLE`, and delegates final open bookkeeping to `vop_stdopen`.

`fifo_read` and `fifo_write` unlock the vnode around socket I/O, take the vnode token, and call `soreceive`/`sosend` with nonblocking flags derived from `IO_NDELAY`.

`fifo_ioctl` forwards ioctls to the underlying read and/or write socket through a temporary `struct file` and `soo_ioctl`.

`fifo_kqfilter` attaches EVFILT_READ and EVFILT_WRITE knotes to the corresponding socket buffer. Read filters report available bytes and EOF/HUP when disconnected; write filters report socket send space and EOF/HUP/NODATA when disconnected.

`fifo_close` decrements reader/writer counts, disconnects peer sockets when a side reaches zero, destroys `fifoinfo` when both counts are zero, and delegates to `vop_stdclose`.

Other vnode ops include `fifo_lookup` returning `ENOTDIR`, `fifo_bmap` identity mapping, `fifo_pathconf` for `LINK_MAX`, `PIPE_BUF`, and `CHOWN_RESTRICTED`, `fifo_advlock` rejecting POSIX/advisory locks, `fifo_printinfo`, and `fifo_badop` panics for impossible filesystem mutations.

Important dependencies: socket layer, UNIX-domain socket connection helper, vnode token/locking, kqueue socket buffer helpers, and filesystem wrappers that embed FIFO behavior.

Notable risks or research hooks: open uses sleep/relock cycles and must preserve counts on interrupt/error. Kqueue detach assumes `vp->v_fifoinfo` remains valid while knotes are attached.
