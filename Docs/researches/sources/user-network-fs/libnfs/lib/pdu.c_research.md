# sources/user-network-fs/libnfs/lib/pdu.c

## Purpose

`sources/user-network-fs/libnfs/lib/pdu.c` implements ONC RPC PDU lifecycle management for libnfs. It owns RPC queue primitives, PDU allocation and freeing, XID assignment and lookup, timeout stamping, send queueing over TCP, UDP, broadcast, server, TLS-start, and GSS-authenticated modes, reply decoding, server-side call dispatch, reply construction, cancellation, and top-level PDU processing. The source was read as a complete 1335-line file for this report.

## Important APIs, Types, and Functions

Queue utilities are `rpc_reset_queue`, `rpc_enqueue`, `rpc_return_to_outqueue`, `rpc_remove_pdu_from_queue`, and the mutex-wrapped `rpc_remove_pdu_from_queue_unlocked`. XID and lookup utilities are `rpc_hash_xid`, `rpc_set_next_xid`, `rpc_find_pdu`, and `rpc_cancel_pdu`.

Allocation and lifecycle APIs are `rpc_allocate_pdu2`, `rpc_allocate_pdu`, internal `rpc_allocate_reply_pdu`, and `rpc_free_pdu`. `rpc_allocate_pdu2` creates client call PDUs with a marshaling buffer, optional decode buffer area, iovec storage, record-marker slot, RPC header, auth credentials, optional AUTH_TLS flagging, and optional GSS credential/verifier state. `rpc_allocate_reply_pdu` builds server reply PDUs. `rpc_free_pdu` releases decoded ZDR payloads, GSS output buffers, ZDR state, iovectors, cursor buffers, and the PDU itself.

Send and receive APIs are `pdu_set_timeout`, `rpc_queue_pdu`, `rpc_process_pdu`, internal `rpc_process_reply`, and internal `rpc_process_call`. Server reply helpers are `rpc_send_reply`, `rpc_send_error_reply`, `rpc_copy_deferred_call`, and `rpc_free_deferred_call`.

## Control Flow

Client request flow starts with `rpc_allocate_pdu2`, which assigns an XID under `rpc_mutex` when multithreading is enabled, initializes the RPC call header, chooses auth flavor, creates the ZDR encoder, marshals the call message, and adds iovectors for the record marker and encoded header. Callers marshal procedure-specific payload after allocation, then `rpc_queue_pdu` finalizes GSS integrity or privacy wrapping if needed, computes the TCP record marker, stamps enqueue statistics and timeouts, and sends or queues based on transport.

For normal TCP clients, `rpc_queue_pdu` appends the PDU to `rpc->outqueue` and kicks `rpc_write_to_socket` if it is at the head. UDP, broadcast, server-context UDP, and AUTH_TLS NULL RPC paths send immediately or enqueue into `waitpdu` before direct `sendto` or `writev`. Transmitted UDP-like requests are tracked in a hash bucket keyed by XID so later replies can locate the PDU.

Reply flow enters `rpc_process_pdu`. Server contexts decode CALL messages through `rpc_process_call`; client contexts decode replies through `rpc_process_reply`. `rpc_process_reply` maps accepted RPC statuses to libnfs callback statuses, verifies TLS STARTTLS responses when expected, processes GSS verifier and privacy/integrity details, handles zero-copy read completion requirements, updates PDU statistics, and invokes the PDU callback with decoded data or an error string. For zero-copy reads, `pdu->in.base` can defer final completion until the remaining payload is read into caller buffers.

Server call flow decodes an RPC CALL into `_rpc_msg`, finds a registered endpoint by program and version, dispatches a matching procedure after decoding its arguments into endpoint-provided storage, or sends protocol-correct accepted error replies for program unavailable, version mismatch, procedure unavailable, or garbage arguments.

## State and Persistence Behavior

This file maintains in-memory RPC transport state only. Persistent fields include `rpc->xid`, `rpc->outqueue`, hashed `rpc->waitpdu` queues and `waitpdu_len`, `rpc->pdu`, transport mode flags, resiliency timeout fields, server endpoint registrations, authentication state, GSS sequence numbers/context, last successful response time, and statistics callbacks. Individual `rpc_pdu` objects persist across send, wait, retransmit, response decode, callback, and free; they store XID, callbacks, ZDR encoders/decoders, iovec cursors, retry flags, timeout timestamps, read cursors, authentication metadata, and stats.

`rpc_return_to_outqueue` supports retransmission by reinserting a previously transmitted PDU near the front of the output queue, incrementing retransmit statistics, resetting output progress, and resetting the input cursor. `pdu_set_timeout` writes absolute per-PDU timeout and major-timeout deadlines, respecting disabled timeout mode and coarser fallback clocks.

## Dependencies and Integration Points

Direct dependencies include `libnfs-zdr.h` for XDR-like encoding and decoding, public and private libnfs RPC structures, `slist.h`, socket headers, `sys/uio.h` for `writev`, platform compatibility headers, optional `krb5-wrapper.h`, optional TLS constants, and private cursor/iovector helpers such as `rpc_add_iovector`, `rpc_free_iovector`, `rpc_reset_cursor`, and `rpc_free_cursor`.

The file is a central integration point between higher-level NFS/MOUNT/NLM task builders and the socket service layer. Higher layers allocate PDUs, marshal procedure payloads, and receive callbacks. The socket layer drains `outqueue`, fills `rpc->pdu` and fragment buffers, and calls `rpc_process_pdu`. Server mode integrates with registered `rpc_endpoint` procedure tables.

## Risks and Edge Cases

Queue invariants are critical: queues are singly linked with explicit head and tail pointers, and incorrect removal or requeueing can lose PDUs, corrupt wait buckets, or break retransmission. `rpc_return_to_outqueue` intentionally avoids replacing a potentially half-sent head PDU, so changes to socket write progress must preserve this assumption.

Authentication and transport special cases add risk. GSS integrity and privacy rewrite encoded payloads late in `rpc_queue_pdu`; buffer sizing, sequence numbers, verifier validation, and zero-copy read handling must remain consistent. AUTH_TLS NULL RPCs are sent inline and expect a specific STARTTLS verifier; failures must stop the session rather than allowing queued RPCs onto an insecure transport. UDP broadcast keeps PDUs in wait queues differently from normal unicast, so removal conditions must be tested separately.

Memory ownership is split between the PDU allocation block, embedded decode buffer, dynamically allocated iovec arrays, ZDR-allocated decoded payloads, GSS buffers, and zero-copy input cursors. Error paths generally free the PDU immediately, so callers must not reuse a PDU after `rpc_queue_pdu` failure. In `rpc_allocate_pdu2`, failure after dynamic `out.iov` allocation jumps to `failed2` and frees the PDU without `rpc_free_iovector`, so this path relies on allocation layout assumptions and is worth leak testing.

Reply processing invokes callbacks with decoded storage owned by the PDU. Callbacks must finish using that storage before the PDU is freed by the surrounding RPC service lifecycle. Bad or malicious RPC replies can exercise decode errors, rejected messages, unknown accept statuses, GSS verifier failures, and size mismatches in zero-copy paths.

## Test Signals

Useful tests include queue unit tests for empty, singleton, head, middle, tail, missing removal, and requeue-after-head cases; deterministic XID hashing and cancellation tests; TCP send tests that verify record marker size, iovec accounting, and immediate write triggering for head PDUs; UDP, broadcast, and server-context send tests; timeout tests with disabled timeout, initial timeout, repeated timeout, major timeout, and fallback clock behavior; reply decode tests for success, rejected messages, all mapped accept errors, decode failure, and callback status/data; server dispatch tests for program unavailable, version mismatch, proc unavailable, garbage args, and successful procedure dispatch; GSS mode tests for krb5, krb5i, krb5p sequence/verifier/wrap behavior; AUTH_TLS NULL RPC tests for correct STARTTLS verifier and failure cases; zero-copy read tests for delayed completion and KRB5P copyout; and leak/fault-injection tests for every allocation and send failure path.
