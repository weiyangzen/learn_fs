# File Research: sources/os/bsd/netbsd-src/sys/fs/nfs/client/nfs_clnfsiod.c

This file manages NFS client asynchronous I/O daemon threads (`nfsiod`). These workers drain per-mount buffer queues populated by `ncl_asyncio()` in `nfs_clbio.c`.

Key state:
- `ncl_numasync` tracks active async daemon count.
- `ncl_iodwant[]` records per-worker availability.
- `ncl_iodmount[]` records which mount a worker is serving.
- `nfs_asyncdaemon[]` tracks allocated worker slots.
- `ncl_iodmax`, `nfs_iodmin`, and `nfs_iodmaxidle` control worker pool sizing.

Key entry points:
- `sysctl_iodmin()` adjusts the minimum spare nfsiod count and creates workers as needed.
- `sysctl_iodmax()` adjusts the maximum and wakes excess idle workers so they can exit.
- `nfs_nfsiodnew_sync()` creates one worker while holding/releasing `ncl_iod_mutex` safely.
- `ncl_nfsiodnew_tq()` services queued worker-creation tasks.
- `ncl_nfsiodnew()` requests async worker creation via `taskqueue_thread`.
- `nfsiod_setup()` initializes NFS client state and starts the configured minimum worker count at boot.
- `nfssvc_iod()` is the worker loop.

Worker behavior:
- A worker sleeps until assigned a mount and work appears on that mount’s `nm_bufq`.
- It removes buffers from the queue, wakes producers waiting for queue drain, drops `ncl_iod_mutex`, and performs I/O.
- `B_DIRECT` write buffers are sent to `ncl_doio_directwrite()`.
- Normal buffers are sent to `ncl_doio()` with read or write credentials.
- Idle workers above `nfs_iodmin` exit after `nfs_iodmaxidle` seconds.
- Optional `vfs.nfs.defect` lets workers move away from mounts with multiple workers to improve fairness.

Dependencies:
- Closely coupled with `ncl_asyncio()` queueing and with `ncl_doio()`/`ncl_doio_directwrite()` execution.
- Uses `ncl_iod_mutex` as the central lock for pool and queue accounting.
- Exposes sysctls under `_vfs_nfs`.

Research notes:
- This file is the async execution backend for read-ahead, write-behind, and async direct writes.
- Race handling is concentrated around worker sleep/timeout, mount dismount, queue drain wakeups, and changes to `ncl_iodmax`.
