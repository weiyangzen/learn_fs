# sources/user-network-fs/samba/source3/include/ctdbd_conn.h

## Purpose
`ctdbd_conn.h` declares the Samba3 client interface to the CTDB daemon. It covers connection setup, messaging, database attach/migrate/parse/traverse, IP registration/enumeration, controls, service registration, request framing, and async parse operations.

## Important APIs, Types, And Functions
- Connection lifecycle: `ctdbd_init_connection()`, `ctdbd_init_async_connection()`, `ctdbd_reinit_connection()`, `ctdbd_probe()`.
- Connection state access: `ctdbd_vnn()`, `ctdbd_conn_get_fd()`, `ctdbd_socket_readable()`.
- Messaging: `ctdbd_messaging_send_iov()`, `register_with_ctdbd()`, `deregister_from_ctdbd()`.
- Process/IP helpers: `ctdbd_process_exists()`, register/unregister/passed IP callbacks, public/all IP foreach APIs.
- Database operations: `ctdbd_dbpath()`, `ctdbd_db_attach()`, `ctdbd_migrate()`, `ctdbd_parse()`, `ctdbd_traverse()`, async `ctdbd_parse_send/recv()`.
- Control and request framing: `ctdbd_control_local()`, `ctdb_watch_us()`, `ctdb_unwatch()`, `ctdbd_prep_hdr_next_reqid()`, `ctdbd_req_send/recv()`.

## Control Flow
Callers establish a CTDB daemon connection, optionally integrate its fd with tevent using `ctdbd_socket_readable()`, attach databases, migrate keys, parse/traverse records, register message service IDs, and send/receive framed CTDB requests. Async APIs return `tevent_req` objects completed by the event loop.

## State And Persistence
The header declares operations against clustered CTDB state: database locations, record migration, public IP registrations, process liveness, and service registrations. Actual state is held by ctdbd and database backends, not the header.

## Dependencies And Integration Points
It depends on dbwrap, TDB data types, tevent, networking structures, messaging callbacks, and CTDB protocol headers. It is a key integration layer for clustered Samba file serving and databases.

## Risks
Callback signatures must remain stable across CTDB protocol changes. Request iovecs must start with an initialized CTDB header. Database migration and parse operations can affect cluster correctness and require careful error propagation. IP registration callbacks run in event contexts and must not block unexpectedly.

## Test Signals
Cluster integration tests should cover connect/reconnect/probe, message registration and delivery, database attach/migrate/parse/traverse, async request cancellation, public IP enumeration, process liveness, and control error codes.
