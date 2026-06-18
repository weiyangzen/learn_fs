<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/MainNFSD/9p_dispatcher.c -->
# sources/user-network-fs/nfs-ganesha/src/MainNFSD/9p_dispatcher.c

## Purpose
Implements the TCP-side 9P dispatcher and worker queue. It accepts 9P/TCP connections, reads framed messages, queues requests to a fridgethr worker pool, dispatches to the 9P interpreter, and cleans per-connection fid/flush/client state.

## Important APIs, Types, And Functions
- `_9p_worker_init()` and `_9p_worker_shutdown()` manage queue and worker-pool lifecycle.
- `DispatchWork9P()` is the common TCP/RDMA enqueue entry and increments connection refcount.
- `_9p_dequeue_req()`, `_9p_consume_req()`, and `_9p_enqueue_req()` implement producer/consumer queues and waiter signaling.
- `_9p_worker_run()` executes queued requests and updates health dequeue counters.
- `_9p_socket_thread()` owns one TCP connection.
- `_9p_dispatcher_thread()` owns the listen socket and accepts clients.

## Control Flow
The dispatcher creates an IPv6 listen socket with IPv4 fallback and spawns one detached socket manager per accepted connection. The socket thread initializes `_9p_conn`, polls, reads the 4-byte size header and frame body, updates transport stats, registers a flush hook, and calls `DispatchWork9P()`. Workers block on a wait list when queues are empty, splice producer to consumer queues under spinlocks, install an operation context, call `_9p_tcp_process_request()` or `_9p_rdma_process_request()`, free request resources, and decrement connection refs.

## State And Persistence Behavior
State is process-local: queue lists/sizes, waiters, connection fids, flush buckets, `msize`, client refs, health counters, and sockets. No durable persistence. Teardown waits for connection refcount to reach zero before fid cleanup.

## Dependencies And Integration Points
Depends on `9p_req_queue.h`, `fridgethr`, 9P protocol handlers, client manager, server stats, RCU, and `nfs_health_`. Started from `nfs_init.c` and stopped from admin shutdown.

## Risks
- Dispatcher accept loop has no direct shutdown check.
- Framing uses unaligned casts and protocol-endian assumptions.
- Disconnect cleanup can wait indefinitely for worker refcount drain.
- Duplicate `_9prq_mutex` assignment and unused condition variable suggest stale synchronization.

## Test Signals
Test IPv6/IPv4 listen, oversized/short/mid-EOF messages, concurrent clients, flush cleanup, worker shutdown timeout, and disconnect while requests execute.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/MainNFSD/9p_dispatcher.c -->
