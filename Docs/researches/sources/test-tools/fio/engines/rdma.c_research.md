# sources/test-tools/fio/engines/rdma.c

## Purpose
`rdma.c` implements fio's `rdma` ioengine using RDMA CM and libibverbs. It supports memory semantics (`write`, `read`) and channel semantics (`send`, `recv`) over InfiniBand, RoCE, or iWARP. It models the writer as the client and the reader as the server, so jobs are unidirectional and diskless.

## Important APIs, Types, And Functions
`enum rdma_io_mode` defines protocol mode. `struct rdmaio_options` holds host, bind, port, and verb. `struct remote_u` and `struct rdma_info_blk` are control-message payloads for exchanging mode, depth, max block size, and remote memory keys/addresses. `struct rdma_io_u_data` stores per-`io_u` send/recv work requests and SGE. `struct rdmaio_data` owns CM IDs, event channel, PD, CQ, QP, registered control buffers, remote memory table, queued/flight/completed I/O arrays, and random selection state.

Key functions include `fio_rdmaio_setup_connect()` and `fio_rdmaio_setup_listen()` for CM setup, `fio_rdmaio_setup_qp()` for verbs resources, `fio_rdmaio_setup_control_msg_buffers()` for registered control messages, `fio_rdmaio_connect()`/`accept()` for handshakes, `fio_rdmaio_post_init()` for registering fio buffers, `fio_rdmaio_prep()` for per-I/O WR setup, `fio_rdmaio_commit()` for posting queued WRs, and `cq_event_handler()`/`fio_rdmaio_getevents()` for completions.

## Control Flow
`.setup` creates a synthetic file and allocates engine state. `.init` rejects mixed read/write and random workloads, parses legacy `host/port/proto` syntax, checks `RLIMIT_MEMLOCK`, creates RDMA CM resources, and either listens as a server for read jobs or resolves/connects as a client for write jobs. `.post_init` registers each fio buffer as an MR and populates the control message. `.open_file` completes the client/server handshake. `.queue` only stages `io_u`s; `.commit` posts sends or receives and moves accepted requests to the flight array. CQ completions move matching flight entries to the completed array, and `.event` pops them FIFO-style.

## State And Persistence
All state is volatile RDMA connection and memory-registration state. No file data is persisted by fio. For memory semantic tests, the server exports registered local buffers and the client chooses remote buffers randomly for RDMA read/write. Close sends a finish notification for memory semantics before disconnecting.

## Dependencies And Integration Points
The engine integrates with `rdma/rdma_cma.h`, libibverbs, fio buffer MR fields (`io_u->mr`), fio file/open lifecycle, and fio's queue/commit asynchronous model. Flags include `FIO_DISKLESSIO`, `FIO_UNIDIR`, `FIO_PIPEIO`, and `FIO_ASYNCIO_SETS_ISSUE_TIME`.

## Risks
Resource cleanup is incomplete: `fio_rdmaio_cleanup()` only frees `rdmaio_data`; many arrays/MRs/control MRs are not explicitly freed in the cleanup path. `get_next_channel_event()` does not ack unexpected events before returning, which may leak CM events. `fio_rdmaio_setup_listen()` uses `htonl(*o->bindname)` instead of parsing the bind address, which looks suspicious. CQ event accounting (`cq_event_num`) is delicate and can underflow/over-adjust. The engine relies on read/write role conventions that can surprise users.

## Test Signals
Meaningful validation requires paired client/server jobs over real RDMA hardware or software RDMA. Important cases are all four verbs, max block size negotiation failure, memlock limit failure, legacy filename parsing, disconnect/finish notification, and completion matching under iodepth. Static tests should inspect cleanup leaks and bind address handling.
