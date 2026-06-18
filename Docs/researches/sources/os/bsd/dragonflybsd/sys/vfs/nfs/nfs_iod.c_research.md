# File Research: sources/os/bsd/dragonflybsd/sys/vfs/nfs/nfs_iod.c

## Role

Implements per-mount NFS IOD reader and writer kernel threads. These threads drive asynchronous client BIOs, RPC transmission/retransmission, reply processing, shutdown, and wakeup state transitions.

## Major Entry Points

- `nfssvc_iod_reader()` processes requests that have received replies on `nm_reqrxq`.
- `nfssvc_iod_writer()` drains queued BIOs from `nm_bioq` and retransmit/auth work from `nm_reqtxq`.
- `nfssvc_iod_stop1()` marks both IOD directions stopping.
- `nfssvc_iod_stop2()` wakes and waits for both threads to exit.
- `nfssvc_iod_writer_wakeup()` moves the writer from waiting to pending and wakes it.
- `nfssvc_iod_reader_wakeup()` moves the reader from waiting to pending and wakes it.

## Implementation Notes

- Both threads hold the mount token while running their state loops.
- Initial `NFSSVC_INIT` state transitions to `NFSSVC_PENDING`; active loops set state to `NFSSVC_WAITING` until work arrives.
- The reader sleeps only when both the primary request queue and receive queue are empty; otherwise it may call `nfs_reply()` to avoid shutdown hard loops.
- Reader-side reply processing calls `nfs_request()` from `NFSM_STATE_PROCESSREPLY` to `NFSM_STATE_DONE`.
- If reply processing returns `EINPROGRESS`, the request is moved back to the transmit queue for authentication or retransmission work.
- Successful reader completion decrements `nm_bioqlen` and invokes `info->done(info)`.
- The writer throttles new BIO processing when `nm_reqqlen > nfs_maxasyncbio` to avoid exhausting mbufs.
- Dequeued BIOs call `nfs_startio()`, which turns them into RPC requests or synchronous fallback I/O.
- Transmit-queue requests call `nfs_request()` from `NFSM_STATE_AUTH` to `NFSM_STATE_WAITREPLY`.
- Requests that do not enter wait-reply state complete immediately with `info->done(info)` and decrement async BIO accounting.
- Shutdown sets thread pointers to `NULL`, marks state `NFSSVC_DONE`, releases the token, and wakes waiters on the thread pointer.

## Dependencies

Works with `struct nfsmount` queues and state fields, `struct nfsreq`, `struct nfsm_info`, NFS request state machine helpers, `nfs_startio()`, `nfs_reply()`, and async BIO accounting used by `nfs_bio.c`.

## Research Notes

This file is small but central to NFS async progress. It separates send-side work from receive-side completion, and `nm_bioqlen` is only decremented when the associated async request reaches a terminal path.
