# File Research: sources/os/bsd/freebsd-src/sys/fs/nfsclient/nfs_clnfsiod.c

`nfs_clnfsiod.c` implements lifecycle management and worker loops for NFS client asynchronous I/O kernel threads (`nfsiod`).

Key contents:
- Defines global worker state: `ncl_numasync`, `ncl_iodwant[]`, and `ncl_iodmount[]`.
- Defines sysctls:
  - `vfs.nfs.iodmaxidle`: idle seconds before non-minimum workers exit.
  - `vfs.nfs.iodmin`: minimum spare workers to keep.
  - `vfs.nfs.iodmax`: maximum worker count.
  - `vfs.nfs.defect`: allow workers to migrate/defect between mounts for fairness.
- `sysctl_iodmin()` validates and applies a new minimum, creating workers synchronously if needed.
- `sysctl_iodmax()` validates and applies a new maximum, waking excess idle workers so they exit.
- `nfs_nfsiodnew_sync()` finds an unused worker slot, creates a kernel process with `kproc_create()`, and marks it available on success.
- `ncl_nfsiodnew_tq()` runs queued worker-creation requests on `taskqueue_thread`.
- `ncl_nfsiodnew()` queues async worker creation and requires the iod mutex.
- `nfsiod_setup()` fetches tunables, initializes client state, clamps initial minimum, and creates initial workers during kernel startup.
- `nfssvc_iod()` is the worker loop: waits for an assigned mount and queued buffers, exits on max shrink/idle timeout, dequeues buffers, calls `ncl_doio()` with read or write credentials, wakes queue waiters as it drains, optionally defects from mounts with multiple workers, and updates global counts on exit.

Important integration points:
- `ncl_asyncio()` in `nfs_clbio.c` queues buffers and wakes/assigns these workers.
- All worker arrays and queue counters are protected by `ncl_iod_mutex` through `NFSLOCKIOD()`.
- Mount buffer queues (`nm_bufq`, `nm_bufqlen`, `nm_bufqiods`, `nm_bufqwant`) are manipulated under the iod lock.
- Worker exit wakes waiters on `ncl_numasync` when the last worker terminates.

Research notes:
- This file is the concurrency backbone for NFS read-ahead and write-behind.
- Risk areas are queue ownership during unmount, worker shrink/idle races, and fairness behavior when multiple mounts share workers.
