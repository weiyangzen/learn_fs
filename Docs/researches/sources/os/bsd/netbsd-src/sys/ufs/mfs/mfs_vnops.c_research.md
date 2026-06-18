# File Research: sources/os/bsd/netbsd-src/sys/ufs/mfs/mfs_vnops.c

This file implements vnode operations for the MFS synthetic block vnode.

Key responsibilities:
- Defines the `mfs_vnodeop_entries` table.
- Implements `mfs_open`, validating block vnode use.
- Implements `mfs_strategy`, routing buffers either directly to kernel miniroot memory, to the current MFS server process, to shutdown bitbucket behavior, or into the queued buffer list.
- Implements `mfs_doio`, copying between buffer data and the MFS backing address using `copyin`/`copyout`.
- Implements identity `mfs_bmap`.
- Implements `mfs_close`, draining pending I/O, invalidating buffers, and signaling shutdown.
- Implements inactive/reclaim/print helpers.

Important behavior:
- If `mfs_proc == curproc`, I/O is handled directly to avoid deadlock through the queue.
- During shutdown, writes are discarded and reads warn.
- Lifetime is protected by `mfs_refcnt`; final reclaim/start-loop exit frees queue, cv, and node.
