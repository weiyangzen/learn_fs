# sources/user-network-fs/samba/source3/smbd/smbXsrv_client.c

## Purpose
This file manages the global SMBX client identity record for an smbd client and implements SMB3 multichannel negotiate ownership transfer. It persists one client record keyed by client GUID, coordinates which smbd process owns that GUID, passes accepted sockets to the owner process when possible, or asks the current owner to disconnect so another process can take over.

## Important APIs, Types, And Functions
`struct smbXsrv_client_table` holds local client counts and the global watched DB context. `smbXsrv_client_global_init()` opens `smbXsrv_client_global.tdb` under the lock path with watched-db support; the comments note that this database contains secret information such as client keys.

`smbXsrv_client_global_id_to_key()` converts a client GUID to the fixed 16-byte TDB key. `smbXsrv_client_global_fetch_locked()` locks a specific client record. `smbXsrv_client_global_verify_record()` parses the NDR `smbXsrv_client_globalB` value, validates version 0, deletes records for explicitly dead or nonexistent server ids, returns free/existing state, and can return the parsed global record plus sequence number.

`smbXsrv_client_create()` builds the per-process client object, initializes the table, sets multi-channel state, stores initial connect time and server id, installs destructors, and starts two long-lived filtered messaging reads for `MSG_SMBXSRV_CONNECTION_PASS` and `MSG_SMBXSRV_CONNECTION_DROP`.

`smb2srv_client_mc_negprot_send()`, `smb2srv_client_mc_negprot_next()`, `smb2srv_client_mc_negprot_done()`, and `smb2srv_client_mc_negprot_watched()` implement the multichannel negotiate state machine for a new connection with an already-known client GUID. `smb2srv_client_connection_pass()` serializes the original negotiate request and sends the TCP socket fd to the owning process if local. `smb2srv_client_connection_drop()` sends a takeover/drop message when the owner is not local.

`smbXsrv_client_connection_pass_loop()` receives passed sockets, validates the pass blob, acknowledges with `MSG_SMBXSRV_CONNECTION_PASSED`, adds the connection with `smbd_add_connection()`, marks the client GUID verified, and replays the captured negotiate request into `smbd_smb2_process_negprot()`. `smbXsrv_client_connection_drop_loop()` validates drop messages and calls `smbd_server_disconnect_client()`.

`smbXsrv_client_remove()` locks and deletes the global client record during teardown after cancelling message loops.

## Control Flow
On initial client creation, no global record is necessarily stored until the SMB2 client GUID is known and verified. In multichannel negotiation, `smb2srv_client_mc_negprot_next()` locks the GUID record and verifies it. If the record is free, it stores the current client global record, marks the GUID verified, and completes.

If another live process owns the GUID, the code avoids duplicate socket delivery by tracking `sent_server_id`. For a local owner process, it opens a filtered read waiting for `MSG_SMBXSRV_CONNECTION_PASSED`, sends a pass message with one fd and the original negotiate request, and then watches the DB record. For a remote/nonlocal owner, it sends a drop message so that the owner disconnects and removes the record, waking watchers.

Watched DB sequencing is used for fairness. If the sequence number changed, this waiter removes and re-adds its watch instance so other waiters can progress. When the watched record changes, the state machine re-locks and re-verifies the record.

The receiving owner process continuously listens for pass and drop messages. The pass loop validates GUIDs and connect times, acknowledges the origin, consumes the fd into a new `smbXsrv_connection`, extracts the original SMB2 message id from the captured negotiate request, and processes negotiation. The drop loop validates identity and disconnects all client connections so another process can acquire the GUID record.

## State And Persistence Behavior
Persistent state is the watched TDB record in `smbXsrv_client_global.tdb`, keyed by client GUID and containing NDR-encoded `smbXsrv_client_global0` plus a sequence number. The stored record tracks client GUID, server id, connect times, addresses, names, and other client-global authentication/session material from generated NDR structures.

Local state includes the `smbXsrv_client` object, current message loops, `server_multi_channel_enabled`, `next_channel_id`, raw event and messaging contexts, and the stored flag on the global record. Records are removed when the client is torn down, and stale records are deleted if their server id no longer exists.

The pass/drop messaging protocol transfers live socket file descriptors and captured negotiate bytes between smbd processes. Correct fd ownership is enforced by setting `rec->num_fds = 0` after successful consumption and closing any unconsumed fds on the `next:` path.

## Dependencies And Integration Points
The file depends on dbwrap, watched dbwrap, Samba messaging with fd passing, tevent, generated NDR for SMBXSRV structures, server-id liveness checks, global messaging context, tsocket transport descriptors, SMB2 negotiate processing, smbd connection add/disconnect functions, authentication/session structures, and multi-channel server policy helpers.

It integrates directly with SMB2 negotiation: this is the code that decides whether a new transport connection for a client GUID is accepted locally, passed to an existing owner, or causes a disconnect/takeover sequence.

## Risks And Edge Cases
This file is race-sensitive. Duplicate pass messages for the same fd can create multiple `smbXsrv_connection` objects for one TCP connection, so `sent_server_id` and watcher ordering are critical. Stale server-id cleanup must be correct or client GUIDs can remain permanently owned by dead processes.

Security and correctness risks include malformed NDR records, invalid message versions, GUID/connect-time mismatches, failing to close passed fds on error paths, storing secret client state in a database with incorrect permissions, and accepting a negotiated connection into the wrong client object.

Cluster or nonlocal behavior is delicate. Local owners receive sockets through fd passing; nonlocal owners receive drop messages and must remove state to let the new process proceed. Any missed watch wakeup, sequence handling bug, or failed global-record removal can stall multichannel negotiation.

## Test Signals
Test signals include SMB3 multichannel negotiate/reconnect torture tests, repeated simultaneous connections with the same client GUID, owner process death during negotiation, pass-message fd leak checks, drop/takeover behavior, watched-db wakeups under contention, malformed/corrupt `smbXsrv_client_global.tdb` records, and verification that session keys and message-id validation remain correct after socket pass.
