# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_session.c

## Purpose

`smb_session.c` implements SMB session transport, request receive/dispatch, session object lifecycle, cancellation, tree/user lookup and teardown, NetBIOS session setup, SMB-over-TCP/NBT headers, keepalive tracking, and SMB request allocation/freeing.

## Main Interfaces

- Transport send/receive: `smb_session_send()`, `smb_session_xprt_gethdr()`.
- Session receiver: `smb_session_receiver()` and internal `smb_session_reader()`.
- Session lifecycle: `smb_session_create()`, `smb_session_delete()`, `smb_session_disconnect()`, `smb_session_logoff()`.
- Request lifecycle: `smb_request_alloc()`, `smb_request_free()`, `smb_request_cancel()`, `smb_session_cancel_requests()`.
- Lookup helpers: `smb_session_lookup_uid()`, `smb_session_lookup_ssnid()`, `smb_session_lookup_uid_st()`, `smb_session_lookup_tree()`.
- Cleanup helpers: `smb_session_close_pid()`, `smb_session_disconnect_owned_trees()`, `smb_session_disconnect_share()`.
- Client/oplock helpers: `smb_session_getclient()`, `smb_session_isclient()`, `smb_session_oplocks_enable()`, `smb_session_levelII_oplocks()`.
- Timers: `smb_session_timers()`.

## Behavior And Data Flow

`smB_session_receiver()` optionally handles a NetBIOS session request on port 139, transitions the session to established, starts an authentication timeout, and calls `smb_session_reader()`. When reading ends, it marks the session disconnected unless already terminated, cancels the auth timeout, shuts down the socket, and calls session cancellation.

The reader loops over 4-byte transport headers, handles keepalives, validates message length, allocates an SMB request, receives the full message into an mbuf chain, accounts received bytes, and calls the session's `newrq_func`. Initially `newrq_func` is `smbsr_newrq_initial()`, which accepts only SMB1 or SMB2 negotiate magic and then lets the SMB1/SMB2 negotiate path install the appropriate request posting function.

Transport send prepends a 4-byte NBT/direct-hosted SMB header, encodes the type/length for port 139 or port 445 semantics, sends mbufs, and always consumes/frees the provided mbuf chain. Header receive validates direct-hosted type zero on port 445.

Session creation allocates id pools, lists, transmit state, locks, random challenge/session keys, copies current server config, records socket addresses and ports for real connections, increments server NBT/TCP counters, and sets command/reply maxima. A special socketless server session is created for server-internal activity and uses a modern dialect/config without map/unmap upcalls.

## Cancellation And Teardown

`smB_request_cancel()` transitions request states carefully. Waiting states require a non-null cancel method; the cancel method runs without holding `sr_mutex`, then the canceller broadcasts the state cv. Completed/cancelled/free-state behavior is explicitly separated.

Session cancellation cancels all outstanding requests, disconnects `IPC$` trees to unblock pipe reads, waits for the request list to empty, closes transaction state objects, and logs off all users. `smb_session_logoff()` walks users, logs off logging-on/logged-on users, waits briefly for user objects to disappear, marks the session shutdown if the user list empties, then disconnects remaining trees.

Tree disconnect helpers post destructors to list flush queues so potentially blocking unmap/disconnect operations do not run while holding list locks. Share-specific disconnect also cancels requests using the affected tree.

## Dependencies

This file depends on kernel sockets, SMB network send/receive mbuf helpers, NetBIOS name parsing, SMB1/SMB2 negotiate entry points, request queues, session/user/tree/ofile state machines, task cancellation, durable handle/session logoff behavior, random number generation, and server counters/config.

## Notable Invariants And Risks

- New requests are allowed only while session state is connected/initialized/established/negotiated.
- Every allocated request is inserted into `s_req_list` and removed during `smb_request_free()`.
- Request free releases ofile, tree, user, tree-connect user, request-specific memory, and mbuf chains.
- Authentication timeout protects sessions with no authenticated users.
- Keepalive timer decrement is currently incomplete; comments note idle-session killing is not implemented.
- `smb_reader_delay` exists only to serialize request dispatch for smbtorture workarounds.
- Cancellation correctness depends on each waiting state installing exactly one valid `cancel_method`.
