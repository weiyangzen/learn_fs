# sources/user-network-fs/samba/source3/torture/test_ctdbd_conn.c

Purpose: This file stress-tests asynchronous CTDB daemon request/response handling through Samba's `ctdbd_connection` layer. It repeatedly sends CTDB `CTDB_CONTROL_ECHO_DATA` controls with random payloads and validates echoed replies while running multiple requests in parallel.

Important APIs/types/functions: `struct ctdb_echo_state` owns a `ctdb_req_control_old`, two iovecs, and expected echo data. `ctdb_echo_send()` constructs a CTDB control request, uses `ctdbd_prep_hdr_next_reqid()`, and sends it with `ctdbd_req_send()`. `ctdb_echo_done()` validates operation, status, data length, and payload bytes from `ctdbd_req_recv()`. `ctdb_ping_flood_send()` maintains a parallel request window until a timed wakeup marks the flood done. The public test is `run_ctdbd_conn1()`.

Control flow: `run_ctdbd_conn1()` creates a Samba tevent context, opens an async CTDB connection using `lp_ctdbd_socket()`, starts `ctdb_ping_flood_send()` with `torture_nprocs` parallel requests and a duration derived from `torture_numops`, then polls and receives the aggregate result. Each completed echo starts another echo until the timer fires; after the timer, the request completes once all in-flight echoes drain.

State/persistence behavior: This is a transient IPC test. Request ids are allocated on the CTDB connection, echo payloads are talloc-owned buffers with random content, and no durable database state is written by the test itself. Persistence concerns are limited to CTDB daemon request queues and socket state.

Dependencies and integration points: It depends on `ctdbd_conn.h`, cluster support, CTDB protocol definitions, `tevent_unix`, and global torture knobs `torture_nprocs` and `torture_numops`. It integrates with clustered Samba deployments and validates the async CTDB client path used by source3 components.

Risks: The test requires a reachable CTDB daemon and valid `lp_ctdbd_socket()`; standalone non-clustered environments will fail setup. Random payload sizes and concurrent request churn expose ordering and lifetime bugs, but also make failures sensitive to CTDB load and timeout settings.

Test signals: Passing requires every echo reply to be `CTDB_REPLY_CONTROL`, status zero, same datalen, and byte-identical payload. Failures print reqid, errno, wrong operation, nonzero status, length mismatch, or data mismatch.
