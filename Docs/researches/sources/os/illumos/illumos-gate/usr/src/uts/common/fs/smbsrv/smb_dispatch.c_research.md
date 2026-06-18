# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_dispatch.c

## Role

Central SMB1 request dispatcher. It defines the SMB command table, handles request queueing, cancellation, SMB header decoding, UID/TID setup, AndX command chaining, reply construction/signing, error mapping, and SMB1 request statistics.

## Major Responsibilities

- Maps every SMB command byte to a name, pre-op, main handler, post-op, minimum dialect, and dispatch flags.
- Performs early SMB header peek in the reader thread for signing sequence handling and `SMB_COM_NT_CANCEL`.
- Dispatches most SMB1 requests to the server worker task queue.
- Executes cancellation in the reader thread when enabled.
- Decodes each SMB command block into VWV and data shadow chains.
- Handles SMB signing verification and reply signing.
- Looks up user and tree objects unless suppressed by command flags.
- Executes command pre/main/post hooks and cleans up transaction state.
- Implements AndX reply backpatching and chained-command continuation.
- Encodes normal and error replies and disconnects malformed clients when required.
- Tracks per-command received bytes, transmitted bytes, request count, and latency.

## Key Functions

- `smb1sr_newrq()` peeks the SMB header, maintains signing sequence numbers, handles fast cancel dispatch, and queues requests.
- `smb1_tq_work()` moves requests from wait queue to run queue and invokes SMB1 work.
- `smb1sr_work()` is the main SMB1 command execution loop, including header decode, signing check, command decode, UID/TID binding, command dispatch, AndX processing, and reply/error handling.
- `smbsr_cleanup()` releases transaction references and marks requests cleaned.
- `smbsr_encode_empty_result()` and `smbsr_encode_result()` encode handler replies.
- `smbsr_check_result()` validates encoded reply structure and patches variable byte counts.
- `smbsr_decode_vwv()` and `smbsr_decode_data()` decode command parameter/data chains with SMB error setup on failure.
- `smbsr_send_reply()` rewrites the SMB header, signs if enabled, and sends the reply.
- `smbsr_map_errno()`, `smbsr_errno()`, `smbsr_status()`, and `smbsr_set_error()` translate and install SMB1 error state.
- `smbsr_lookup_xa()`, `smbsr_lookup_file()`, and `smbsr_release_file()` manage common request-associated objects.
- `smb_com_invalid()` handles unsupported or invalid SMB commands.
- `smb_dispatch_stats_init()`, `smb_dispatch_stats_fini()`, and `smb_dispatch_stats_update()` manage SMB1 kstat data.

## Research Notes

This file is the SMB1 control plane. Its most important invariant is that every non-kept request is cleaned and freed exactly once, while malformed protocol state can force a session disconnect. AndX chaining is implemented by moving the request chain offset to the next command and backpatching the prior reply block.
