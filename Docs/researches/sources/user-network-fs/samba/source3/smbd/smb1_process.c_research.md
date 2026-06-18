# sources/user-network-fs/samba/source3/smbd/smb1_process.c

## Purpose
`smb1_process.c` is the central SMB1 packet-processing loop for smbd. It receives and validates SMB1 packets, verifies signing and encryption, dispatches commands through the SMB1 command table, manages AndX chaining, sends responses, queues deferred opens, limits outstanding transaction state, sends keepalives, and optionally runs a forked SMB echo handler that can answer one-reply echo probes while forwarding non-echo traffic to the parent smbd.

## Important APIs, types, and functions
- `struct pending_message_list` stores deferred SMB1 open requests, including original request time, connection pointers, sequence number, encryption flag, copied input buffer, and optional deferred-open metadata.
- `smbd_echo_init()`, `smbd_lock_socket()`, and `smbd_unlock_socket()` initialize and coordinate the optional async echo handler's cross-process socket lock, using a robust process-shared mutex when available or an fcntl lock file otherwise.
- `smb1_srv_send()` signs, optionally encrypts, and writes an SMB1 response to the transport socket while holding the echo-handler socket lock.
- `receive_smb_raw_talloc()`, `receive_smb_raw_talloc_partial_read()`, and `smb1_receive_talloc()` read SMB1 packets, implement the large WriteAndX partial-read optimization, decrypt encrypted packets, and verify SMB1 signatures.
- `push_deferred_open_message_smb1()` and `push_queued_message()` copy a request into `sconn->deferred_open_queue` for later processing.
- `allow_new_trans()` rejects duplicate transaction MIDs and caps pending transaction requests to reduce memory-DoS exposure.
- `smb_messages[256]` maps SMB command bytes to names, reply handlers, and dispatch flags such as `AS_USER`, `NEED_WRITE`, `CAN_IPC`, `AS_GUEST`, and `DO_CHDIR`.
- `switch_message()` validates negotiation/session/tree context, changes process credentials/service directory, enforces write/IPC/encryption requirements, updates session/tcon crypto flags for smbstatus, and invokes the selected reply function.
- `construct_reply()`, `construct_reply_chain()`, `smb_request_done()`, and `process_smb1()` build request objects, handle normal versus AndX-chained dispatch, splice chained responses, and ship final replies.
- `smb1_is_chain()`, `smb1_walk_chain()`, `smb1_chain_length()`, and `smb1_parse_chain()` inspect and materialize SMB1 AndX request chains with strict offset and length validation.
- `smbd_smb1_server_connection_read_handler()` is the event-loop read entry point for SMB1 sockets and the echo-handler trusted pipe.
- `keepalive_fn()` sends SMB1 NetBIOS keepalives for non-SMB2 connections.
- `fork_echo_handler()` and its helpers (`smbd_echo_read_send()`, `smbd_echo_reply()`, `smbd_echo_loop()`, `smbd_echo_got_packet()`) implement the optional forked echo responder and forwarding channel.
- `req_is_in_chain()` reports whether a request is an AndX chain member or the head of a still-chained packet.

## Control flow
Incoming SMB1 I/O enters through `smbd_smb1_server_connection_read_handler()`. When async echo handling is enabled, it prefers packets already forwarded by the echo child and locks the socket when reading directly from the client so parent and child do not race. It calls `receive_smb_talloc()` with trusted-channel awareness; in this source tree that resolves to the SMB1 receive implementation, which reads the NetBIOS length, optionally performs a partial large-WriteAndX read, decrypts packets, and verifies signing. Successful packets are passed to `process_smb()`, which reaches `process_smb1()`.

`process_smb1()` rejects short or invalid SMB headers, with a guarded test-only suicide packet escape, then chooses chained or unchained construction. `construct_reply()` allocates a single `smb_request`, initializes it, and calls `switch_message()`. `construct_reply_chain()` parses all AndX members into linked request objects, dispatches the first, and relies on `smb_request_done()` to continue through the rest of the chain.

`switch_message()` is the dispatch gate. Before negotiation completes, only `SMBnegprot` and legacy mailslot messenger commands are allowed. Unknown or unimplemented commands get `reply_unknown_new()`. Implemented commands are run under the user, guest, or root context implied by the dispatch flags. For user commands it requires a valid tree connection, sets case-sensitivity policy from the service and client flags, calls `change_to_user_and_service()`, enforces write permissions and IPC restrictions, and checks service encryption requirements. It also updates session and tree encryption/signing status flags, persisting those global records when needed, then invokes the command handler from `smb_messages`.

`smb_request_done()` is both the normal response shipper and the continuation mechanism for AndX chains. For chained requests it finds the completed request, dispatches later chain members while earlier responses are successful, propagates UID/TID and `chain_fsp`, then appends each subresponse with `smb_splice_chain()`. It finally copies the last response's UID/TID/error-code style/error values to the first response, fixes the SMB length, signs/encrypts as needed, sends with `smb1_srv_send()`, and frees either the single request or the request array.

The chain parser walks the initial command and each AndX link using offsets from the SMB header. It rejects non-growing offsets, offsets beyond the total packet, too-short word arrays, and byte counts that would exceed the packet. Response splicing performs the inverse operation, aligning appended word-count fields to a 4-byte boundary and specially fixing ReadAndX data offsets after appending.

When the optional echo handler is forked after negotiation, the child waits for client readability, gives the parent one second to handle the packet, then locks the shared socket and reads if the parent did not. One-reply `SMBecho` probes are answered directly by the child. Any other SMB packet has its sequence number placed into the SMB security-signature field and is forwarded over a pipe to the parent, where the parent read handler treats the pipe as a trusted channel.

## State and persistence behavior
Persistent protocol state is held outside this file in `smbXsrv_connection`, sessions, tree connections, open files, signing/encryption contexts, and the smbd server connection. This file mutates that state by updating session/tcon crypto flags, connection encryption requirements, per-connection operation counts, deferred-open queues, echo-handler descriptors, echo-handler shared lock state, and transport status-dependent I/O behavior.

Most allocations are request-scoped with `talloc`; async handlers signal suspension by clearing `req->outbuf` and later call `smb_request_done()`. Deferred opens copy the full input buffer into a `pending_message_list` so processing can resume after oplock/share-mode conditions change. The echo handler adds process-level state: a child process, a parent pipe, a trusted event fd, a socket lock fd or process-shared mutex, pending `iovec` writes to the parent, and a ref-counted lock protocol to support nested send/read sections.

## Dependencies and integration points
This file is integrated with nearly every SMB1 smbd subsystem: session and tree lookup/update (`smbXsrv_session`, `smbXsrv_tcon`), signing and encryption (`smb1_srv_check_sign_mac`, `smb1_srv_calculate_sign_mac`, `srv_encrypt_buffer`, `srv_decrypt_buffer`), transport I/O helpers, command reply implementations from the SMB1 reply/transaction/printing/IPC code, loadparm configuration, credential switching, message/CTDB support, deferred open records, profiling/debug dump hooks, and the tevent async framework.

Other files call the exported functions declared in `smb1_process.h`: SMB2 receive glue delegates SMB1 packet receive handling to `smb1_receive_talloc()` in mixed negotiation paths; SMB1 transaction implementations use `allow_new_trans()`; negotiation starts `fork_echo_handler()` when async echo is configured; event-loop code calls `smbd_smb1_server_connection_read_handler()`; named-pipe callbacks call `smb_request_done()` or `smb1_srv_send()`.

## Risks and edge cases
- Packet length, AndX offset, and byte-count validation are security-critical because this file parses untrusted network input and performs pointer arithmetic into request buffers.
- The large WriteAndX partial-read optimization intentionally drains unread payload and spoofs a shorter SMB buffer; regressions can corrupt subsequent packet framing or break zero-copy write paths.
- Signing/encryption sequencing depends on correct sequence numbers, trusted-channel handling for echo-forwarded packets, and consistent final send encryption decisions.
- `switch_message()` combines authentication, service chdir, IPC restrictions, write checks, encryption policy, and dispatch; small flag mistakes in `smb_messages` can expose commands under the wrong credentials or tree type.
- AndX chaining across async handlers is fragile: suspended requests must preserve the request array, `chain_fsp`, input buffer ownership, and response-success state until `smb_request_done()` resumes.
- `smb_splice_chain()` has to maintain 16-bit response-size constraints except for WriteX and has a special ReadAndX offset fixup that is easy to break.
- The echo handler uses fork, shared locks, pipes, event fds, and direct SMB replies from a child process; lock leaks or incorrect trusted-channel decisions can race socket reads, duplicate replies, or desynchronize signing state.
- `allow_new_trans()` caps only after `count > 5`, allowing six existing entries before rejecting the next request; callers should understand that exact threshold.
- Debug packet dumping writes to `/tmp` at high debug levels, so it is useful for diagnosis but sensitive in production due to packet contents.

## Test signals
Strong signals include Samba selftests that exercise SMB1 negotiation, session setup, tree connect, signed/encrypted SMB1 traffic, IPC and transaction commands, deferred open behavior, AndX command chains, large WriteAndX requests, invalid malformed chains, and async echo handling. `source3/torture/vfstest_chain.c` directly references `smb1_parse_chain()` with canned chain data. Useful targeted tests would fuzz `smb1_walk_chain()` offsets/lengths, assert `smb_request_done()` chained error propagation, verify `allow_new_trans()` duplicate and limit behavior, and run echo-handler tests with signing enabled and disabled.
