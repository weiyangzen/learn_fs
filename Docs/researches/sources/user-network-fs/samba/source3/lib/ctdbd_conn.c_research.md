# sources/user-network-fs/samba/source3/lib/ctdbd_conn.c

Purpose: implements Samba's low-level connection to the CTDB daemon for cluster messaging, controls, database attach/traverse/fetch/migrate, IP registration/enumeration, probing, and async request handling.

Important APIs/types/functions: private `struct ctdbd_connection` and callback table; public connection init/reinit/async init, `ctdbd_vnn()`, `ctdbd_conn_get_fd()`, `register_with_ctdbd()`, `deregister_from_ctdbd()`, `ctdbd_messaging_send_iov()`, `ctdbd_control_local()`, `ctdbd_db_attach()`, `ctdbd_dbpath()`, `ctdbd_migrate()`, `ctdbd_parse()`, `ctdbd_traverse()`, IP register/unregister/pass/foreach helpers, watch/unwatch, probe, `ctdbd_req_send/recv()`, and `ctdbd_parse_send/recv()`.

Control flow: initialization opens a Unix socket, gets local PNN/VNN, validates node activity via nodemap, registers a random srvid, and optionally creates nonblocking async queues. Synchronous controls/calls write CTDB packets and loop reading replies while dispatching intervening messages. Async requests enqueue writes, maintain pending requests by reqid, run one packet read at a time, and complete matching tevent requests. Traversal starts a CTDB traverse and consumes message records until an empty key/data marker.

State and persistence: per-connection fd, reqid counter, callback array, random service id, outgoing queue, pending requests, and active read request. Persistent cluster state lives in CTDB daemon databases and node maps, not in this file.

Dependencies/integration: CTDB protocol structs/opcodes, tevent, Samba messaging, dbwrap RBT for IP collation, Unix sockets, poll/read/write helpers, talloc, fault handling. `cluster_fatal()` exits immediately on daemon I/O failure to release process IDs quickly.

Risks/test signals: sync calls are rejected when async requests are pending on the same connection; daemon read/write errors terminate the process; packet validation is minimal in async receive beyond length. IP aggregation must handle inactive/deleted nodes and duplicate public IP views. Tests should cover reqid wrap, mismatched replies, message callback dispatch, timeout/probe, async cancellation/pending cleanup, traverse end markers, malformed public IP payloads, IPv4-mapped IPv6 canonicalization, and fatal-path behavior under socket loss.
