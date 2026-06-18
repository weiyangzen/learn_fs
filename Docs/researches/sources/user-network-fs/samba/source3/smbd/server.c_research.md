# sources/user-network-fs/samba/source3/smbd/server.c

## Purpose

`server.c` is the main smbd parent-process implementation and program entry point. It parses daemon options, initializes global Samba state, starts helper daemons, opens listening sockets for configured SMB transports, accepts clients, forks per-client smbd children, supervises children, fans out parent messages, handles dynamic address changes, and runs the parent tevent loop. It is the central lifecycle coordinator for source3 file serving.

## Important APIs, Types, And Functions

Key local types are `struct smbd_parent_context`, `struct smbd_open_socket`, and `struct smbd_child_pid`. The parent context owns the event and messaging contexts, configured transports, listener list, child PID list, helper daemon server IDs, cleanup timer state, and optional QUIC TLS parameters.

Important functions include `main()`, `open_sockets_smbd()`, `smbd_open_one_socket()`, `smbd_accept_connection()`, `smbd_parent_loop()`, `smbd_setup_sig_chld_handler()`, `remove_child_pid()`, `smbd_notifyd_init()`, `cleanupd_init()`, `smbd_claim_version()`, `smbd_init_addrchange()`, `smbd_addr_changed()`, `smbd_parent_conf_updated()`, `smbd_msg_debug()`, and message fan-out helpers such as `messaging_send_to_children()`.

## Control Flow

`main()` initializes talloc, locale, smbd shims, globals, command-line parsing, logging, random source validation, security context state, signals, clustering, event and messaging contexts, `smb.conf`, loadparm context, daemonization, parent context allocation, transports, optional QUIC TLS state, signal handlers, databases, session/tcon/client global tables, locking, leases, notifyd, cleanupd, scavenger, registry, share-info DB, system and guest session info, and global file/open state. It rejects unsupported standalone AD DC mode unless inhibited and claims a cluster-wide Samba version lock when clustered upgrades are not allowed.

For daemon mode, it opens listener sockets according to `server smb transports` or `--port`; for inetd mode, it duplicates fd 0 and directly calls `smbd_process()`. Listener setup binds either configured interfaces only or wildcard IPv6/IPv4 addresses, registers parent messaging handlers, optionally starts mDNS registration, and enters `tevent_loop_wait()`.

On accept, interactive mode handles the connection in-process after reinit. Normal daemon mode checks `max smbd processes`, forks, frees the parent context in the child, reinitializes after fork, optionally performs a synchronous QUIC TLS handshake, and calls `smbd_process()`. The parent closes the accepted fd, records the child PID, and checks log size. `SIGCHLD` reaps exits and `remove_child_pid()` restarts `cleanupd` or `notifyd` if those helper daemons died; ordinary children are stored in `cleanupdb` and may trigger cleanupd.

## State And Persistence Behavior

The file maintains in-memory parent state and process state. It creates pid files, lock/pid/ncalrpc directories, named-pipe directories, global messaging/server/session/tcon/client/open databases, share-info DB handles, locks, memcache, registry state, and helper daemon identities. `smbd_claim_version()` uses `g_lock` to store and hold the running Samba version in a cluster-sensitive lock record. Dynamic interface handling adds/removes listener sockets and sends `MSG_SMB_IP_DROPPED` when a bound address disappears.

## Dependencies And Integration Points

The file integrates with almost every smbd subsystem: loadparm, secrets/passdb, messaging, server IDs, profile, cluster/CTDB, notifyd, cleanupd, scavenger, leases, locking, share modes, registry, DCERPC endpoint setup, QUIC/TLS, socket helpers, mDNS/Avahi/DNSSD, auth session info, global contexts, and child `smbd_process()`. Parent message handlers propagate config reloads, debug changes, forced tree disconnects, client-kill requests, ID cache invalidations, notify-start events, TLS reloads, and dynamic IP drops to children.

## Risks

This file has high blast radius. Initialization order matters: event context before messaging, password DB before global SAM SID, ncalrpc directory before endpoint mapper races, daemonization before parent-child pipe setup, and QUIC filtering before listener bind. Fork paths must not retain parent-only talloc state. Child-count enforcement depends on reliable SIGCHLD reaping. Helper daemon restart loops can hide repeated startup failures but log them. Listener binding tolerates individual socket failures, but inconsistent partial binding across transports can abort startup. QUIC support depends on compile-time `HAVE_LIBQUIC`, TLS parameter preparation, and runtime enablement.

## Test Signals

Coverage signals include daemon and inetd startup tests, foreground stdin EOF shutdown, reload-on-SIGHUP, parent-to-child message fan-out, max-process limit behavior, helper daemon restart after exit, listener binding under `bind interfaces only`, dynamic address add/drop handling, QUIC requested/enabled/disabled paths, clustered version conflict rejection, and failure injection for database or directory initialization order. Integration tests should observe pidfile creation/removal and successful client fork/process cleanup.
