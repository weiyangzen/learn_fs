# sources/user-network-fs/samba/source3/nmbd/asyncdns.c

## Purpose
`asyncdns.c` provides DNS lookup support for nmbd WINS DNS proxy behavior. When pipes/fork are available, it offloads blocking hostname resolution to a child process; otherwise it performs synchronous DNS lookup inline.

## Important APIs, Types, and Functions
`add_dns_result()` inserts positive or negative DNS answers into the WINS server subnet name cache with different TTLs and sources (`DNS_NAME` or `DNSFAIL_NAME`). In async mode, global fds, child pid, queue/current packet pointers, and `in_dns` track child communication and recursion. `asyncdns_fd()` exposes the read fd. `start_async_dns()` creates pipes, forks, sets signal handling, reinitializes after fork, and runs `asyncdns_process()` in the child. `queue_dns_query()` writes or queues packet queries. `run_dns_queue()` reads child results, updates cache, responds to the current and queued matching packets, frees packets, and starts the next queued query. `kill_async_dns_child()` terminates the child. Sync mode implements `queue_dns_query()` directly with `interpret_addr()`.

## Control Flow
In async mode, nmbd starts the DNS child when configured as WINS server with DNS proxy. Queries are represented as `struct query_record` containing an `nmb_name` and result address. The parent writes one current query to the child and queues additional packets. When the child returns a result, the parent caches it, sends WINS query responses for the current and any queued matching packet, frees them, then dispatches the next queued packet.

## State and Persistence
The DNS answer is persisted in nmbd's in-memory WINS name cache with TTL: one hour for negative answers, two hours for positive answers. Async child/process state is global and process-local. No on-disk persistence is performed here.

## Dependencies and Integration Points
It depends on nmbd packet structures and name cache APIs, Samba pipe/read/write helpers, process-existence checks, `interpret_addr()`, and WINS response functions. It is compiled with `SYNC_DNS` when `HAVE_PIPE` is missing.

## Risks
Global queue state and packet locking must be correct to avoid leaks or double frees. If the child dies, `run_dns_queue()` closes fds and restarts it, but pending current/queued behavior around restart is delicate. DNS replies are keyed by NetBIOS name equality; queued identical questions all receive the same result. The child exits on pipe errors without cleanup beyond process exit.

## Test Signals
Tests should cover positive and negative cache insertion TTL/source, async queue ordering, duplicate queued query fanout, child death/restart, write/read failure handling, `in_dns` recursion guard, packet lock clearing, sync-mode behavior, and SIGTERM child cleanup.
