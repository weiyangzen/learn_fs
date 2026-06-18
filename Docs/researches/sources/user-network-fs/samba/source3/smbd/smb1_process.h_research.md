# sources/user-network-fs/samba/source3/smbd/smb1_process.h

## Purpose
`smb1_process.h` declares the exported SMB1 processing functions shared across smbd. It exposes packet receive/send helpers, AndX chain parsing utilities, request completion, transaction throttling, echo-handler setup, deferred-open requeueing, keepalive handling, and the main SMB1 processing entry points.

## Important APIs, types, and functions
- `smb1_srv_send()` sends an SMB1 response buffer with optional signing and encryption.
- `allow_new_trans()` validates that a new transaction MID is not duplicated and that pending transaction state remains bounded.
- `smb_request_done()` completes a request, including chained-request continuation and final response send.
- `smb_fn_name()`, `add_to_common_flags2()`, and `remove_from_common_flags2()` expose command-name and shared FLAGS2 helpers.
- `smb1_is_chain()`, `smb1_walk_chain()`, `smb1_chain_length()`, and `smb1_parse_chain()` expose SMB1 AndX chain inspection and request materialization.
- `req_is_in_chain()` reports whether a request belongs to an AndX chain.
- `fork_echo_handler()` and `smbd_echo_init()` manage the optional forked echo responder.
- `smb1_receive_talloc()` reads, decrypts, and verifies an SMB1 packet into a talloc buffer.
- `push_deferred_open_message_smb1()` queues a request for later deferred-open processing.
- `process_smb1()`, `construct_reply()`, `smbd_smb1_server_connection_read_handler()`, and `keepalive_fn()` expose the core packet-processing and event-loop hooks.

## Control flow
The header has no executable control flow, but its declarations mirror the principal SMB1 lifecycle. Event-loop code reads with `smbd_smb1_server_connection_read_handler()` or lower-level `smb1_receive_talloc()`, passes packets to `process_smb1()`/`construct_reply()`, dispatches through implementation-private command tables, and completes via `smb_request_done()` or `smb1_srv_send()`. Utility callers can inspect AndX chains before dispatch and can queue deferred opens when a reply needs to wait.

## State and persistence behavior
The declarations operate on long-lived smbd objects (`smbXsrv_connection`, `smbd_server_connection`, `smb_request`, `trans_state`, file IDs, deferred open records), but the header itself owns no storage. Implementations mutate transport state, session/tree crypto flags, deferred-open queues, and echo-handler descriptors.

## Dependencies and integration points
This interface is consumed by SMB1 command handlers, SMB2/SMB1 negotiation glue, transaction handlers, named-pipe code, event-loop setup, and torture tests. It depends on common Samba types such as `TALLOC_CTX`, `NTSTATUS`, `DATA_BLOB`-style buffers through `char **buffer`, `struct timeval`, `struct file_id`, and `struct deferred_open_record`.

## Risks and edge cases
- Several functions have ownership-sensitive contracts: `smb1_receive_talloc()` returns talloc-owned packet buffers, `smb1_parse_chain()` returns a talloc-owned request array, and `smb_request_done()` may free request objects after sending.
- Callers of `smb1_srv_send()` must pass the right signing/encryption flags and sequence number; mistakes affect SMB1 security state.
- Chain-walking callbacks receive pointers into the original SMB buffer and must not outlive it.
- `construct_reply()` and `process_smb1()` are SMB1-specific and should not be used for SMB2 packets despite shared connection structures.

## Test signals
Compile-time coverage should ensure all cross-file users agree on the function signatures. Behavioral signals come from tests of the implementation in `smb1_process.c`: chained request parsing, transaction throttling, deferred open replay, SMB1 receive signing/encryption, echo-handler forwarding, and final response send behavior.
