# sources/user-network-fs/samba/source4/ldap_server/ldap_server.c

## Purpose

`ldap_server.c` implements Samba's LDAP service transport and event-loop layer. It accepts LDAP, LDAPS, global catalog, and LDAPI sockets; manages streams and limits; decodes LDAP PDUs; queues calls; writes replies; handles notifications; reloads TLS certificates; and registers the server service.

## Important APIs, Types, and Functions

Exported symbols are `ldapsrv_recv()`, `ldapsrv_notification_retry_setup()`, and `server_service_ldap_init()`. Important internals include accept/TLS accept handlers, read/process/wait/write/postprocess callbacks, notification retry handling, `add_socket()`, `ldap_reload_certs()`, `ldapsrv_task_init()`, `ldapsrv_post_fork()`, `ldapsrv_before_loop()`, `ldapsrv_check_packet_size()`, and `ldapsrv_packet_check()`.

## Control Flow

Task init requires AD DC role, creates service state, binds configured LDAP/LDAPS/GC/LDAPI sockets, and registers messaging. Accept converts sockets to tstreams, initializes anonymous or system sessions, detects GC ports, initializes backend state, loads query limits, and starts TLS immediately for LDAPS. The read path reads a full LDAP PDU, checks size, decodes ASN.1, queues the call, dispatches through `ldapsrv_do_call()`, waits for async bind/unbind hooks, writes replies through a queued writev path, runs postprocess hooks for TLS/SASL stream switching, and starts the next read.

## State and Persistence Behavior

Service state tracks TLS params, call queue, connections, notification generation/retry, loadparm, messaging, event context, and child SAMDB context. Connection state tracks raw/TLS/SASL streams, active call, pending notification calls, LDB/session state, query limits, timers, and termination reason. Runtime state changes include TLS certificate reload, notification generation, and active stream replacement.

## Dependencies and Integration Points

The file integrates Samba service/task/process APIs, tevent/tstream, TLS, LDAP ASN.1 encode/decode, auth helpers, IRPC name registration, server ID database, SAMDB, interface binding, loadparm limits, and messaging. It orchestrates backend, bind, and extended handlers via shared structures and generated prototypes.

## Risks and Edge Cases

Direct `recv`/`send` callbacks panic because tstream owns I/O after accept. Termination disconnects active TLS/SASL before raw stream. Anonymous and authenticated request size limits differ. Notification calls persist while busy. Large replies are split by 25 MiB and `IOV_MAX`. A failure log uses `ldapi_path` after freeing it, which is a diagnostic lifetime risk.

## Test Signals

Coverage should include LDAP/LDAPS accept, StartTLS and SASL stream switching after response write, request size limits, timeouts, expired Kerberos-session unsolicited disconnect, notifications, TLS certificate reload to prefork workers, GC and LDAPI sockets, and large reply chunking.
